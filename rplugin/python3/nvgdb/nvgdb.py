# ============================================================================
# FILE: nvgdb.py
# AUTHOR: Philip Karlsson Gisslow <philipkarlsson at me.com>
# License: MIT license
# ============================================================================

import os
import subprocess
import zmq
import msgpack

class NvGdb(object):
    def __init__(self, nvim, dbg_print=False):
        self.dbg_print = dbg_print
        self.nvim = nvim
        self.logstr = []
        self.logstr.append('== NvGdb debug log ==')

        self.curr_file = ''
        self.curr_line = 0

        self.sign_id = -1

    def async_set_fpos(self):
        self.nvim.command('e +' + str(self.curr_line) + ' ' + self.curr_file)
        if self.sign_id != -1:
            self.nvim.call('sign_unplace', 'NvGdb',
                          {'id': self.sign_id, 'fname': self.curr_file})
        # Update sign, TODO cont here..
        self.nvim.call('sign_define', 'curr_pc',
                {'text': '▶'})
        self.nvim.call('sign_place', 5000, 'NvGdb', 'curr_pc', self.curr_file, {'lnum': self.curr_line, 'priority': 20})
        self.sign_id = 5000

    def handle_bp_hit(self, fname, line):
        self.curr_file = fname
        self.curr_line = line
        self.nvim.async_call(self.async_set_fpos)

    def serve(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:5678")
        while True:
            raw = socket.recv()

            msg = msgpack.unpackb(raw, raw=False)
            self.log(msg)
            if msg['type'] == 'bp_hit':
                self.handle_bp_hit(msg['file'], msg['line'])

            socket.send(msgpack.packb({'status': True}, use_bin_type=True))

    def handle_event(self, msg):
        self.log(msg.decode())

    def log(self, s):
        s = str(s)
        if self.dbg_print:
            print(s)
        if '\n' in s:
            ns = s.split('\n')
            for i in ns:
                self.logstr.append(i)
        else:
            self.logstr.append(str(s))

    def get_log(self):
        return self.logstr


# Unittest
if __name__ == '__main__':
    class nvim_mockup(object):
        def __init__(self):
            pass
        def command(self, txt):
            print(txt)
        def async_call(self, p):
            pass

    nv = nvim_mockup()
    ng = NvGdb(nv, dbg_print=True)
    ng.serve()
