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
        self.gdb_socket_connected = False

        self.curr_file = ''
        self.curr_line = 0

        self.sign_id = -1

    def gdb_post(self, msg):
        if self.gdb_socket_connected is False:
            context = zmq.Context()
            self.socket = context.socket(zmq.REQ)
            self.socket.connect("tcp://localhost:8765")
            self.gdb_socket_connected = True
        msg_data = msgpack.packb(msg, use_bin_type=True)
        self.socket.send(msg_data)
        raw_resp = self.socket.recv()
        resp = msgpack.unpackb(raw_resp, raw=False)
        return resp

    def update_bp_signs(self, bps):
        self.nvim.call('sign_unplace', 'nvgdb_bps')
        for b in self.nvim.buffers:
            for bp in bps:
                if b.name in bp:
                    line = int(bp.split(':')[1])
                    self.nvim.call('sign_place', 0, 'nvgdb_bps', 'bp', b,
                        {'lnum': line, 'priority': 10})

    def toggle_breakpoint(self, f, l):
        ret = self.gdb_post({'type': 'toggle_breakpoint', 'file':f, 'line':l})
        self.update_bp_signs(ret['breakpoints'])

    def async_set_fpos(self):
        self.nvim.command('e +' + str(self.curr_line) + ' ' + self.curr_file)
        if self.sign_id != -1:
            self.nvim.call('sign_unplace', 'NvGdb',
                          {'id': self.sign_id, 'fname': self.curr_file})
        # These shall be set in the beginning
        self.nvim.call('sign_define', 'curr_pc',
                {'text': '▶'})
        self.nvim.call('sign_define', 'bp',
                {'text': '●'})
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
            ret = self.handle_event(msg)
            socket.send(msgpack.packb(ret, use_bin_type=True))

    def handle_event(self, msg):
        if msg['type'] == 'bp_hit':
            self.handle_bp_hit(msg['file'], msg['line'])
        return {'status': True}

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

    def stop(self):
        self.log('stop')

    def resume(self):
        self.log('resume')

    def single_step(self):
        self.log('single_step')

    def step_over(self):
        self.log('step_over')

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
