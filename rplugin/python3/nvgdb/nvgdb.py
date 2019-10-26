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

    def async_set_fpos(self):
        self.nvim.command('e +' + str(self.curr_line) + ' ' + self.curr_file)

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
