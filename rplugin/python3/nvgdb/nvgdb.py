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

    def socket_communicate(self, data):
        self.socket.send(data)
        numb = self.socket.poll(200)
        if 0 == numb:
            # FIXME, Add more error handling?
            self.socket.close(linger=True)
            self.gdb_socket_connected = False
            return None
        else:
            raw_resp = self.socket.recv()
            return raw_resp

    def gdb_post(self, msg):
        if self.gdb_socket_connected is False:
            context = zmq.Context()
            self.socket = context.socket(zmq.REQ)
            self.socket.connect("tcp://localhost:8765")
            self.gdb_socket_connected = True
        msg_data = msgpack.packb(msg, use_bin_type=True)
        raw_resp = self.socket_communicate(msg_data)
        if raw_resp != None:
            resp = msgpack.unpackb(raw_resp, raw=False)
        else:
            resp = None
        return resp

    def update_bp_signs(self, bps):
        self.nvim.call('sign_unplace', 'nvgdb_bps')
        for b in self.nvim.buffers:
            for bp in bps:
                if b.name in bp:
                    line = int(bp.split(':')[1])
                    self.nvim.call('sign_place', 0, 'nvgdb_bps', 'bp', b,
                        {'lnum': line, 'priority': 10000})

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
        self.nvim.call('sign_place', 5000, 'NvGdb', 'curr_pc', self.curr_file, {'lnum': self.curr_line, 'priority': 10001})
        self.sign_id = 5000

    def async_floating_window(self):
        lines = self.floating_window_text.split('\n')
        height = len(lines)
        width = max(len(x) for x in lines)
        self.nvim.call('NvGdbFloatingWindow', lines, width, height)

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
        elif msg['type'] == 'eval_word_callback':
            self.floating_window_text = str(msg['data'])
            self.nvim.async_call(self.async_floating_window)
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

    def spawn_stacktrace_window(self, stacktrace):
        self.nvim.command('split NvGdbStackTrace')
        self.nvim.command('setlocal buftype=nofile')
        self.nvim.command('setlocal filetype=NvGdbStackTrace')
        self.nvim.command('bp')
        self.nvim.command('wincmd j')
        self.nvim.command('bp')
        wl = 10
        if len(stacktrace) < 10:
            wl = len(stacktrace)
        self.nvim.current.buffer[:] = stacktrace
        self.nvim.current.window.height = wl
        self.nvim.command('wincmd k')
        # Select first frame and go there..

    #########################
    # Commands implementation
    #########################

    # TO IMPLEMENT (USPs for this plugin)
    # 1.) Show variable value in floating windows (sort of done..)
    # 2.) Show call stack in new window and be able to navigate it - (currently working on..)
    #     - Need auto command to navigate it (move up and down frames..)
    # 3.) radare2 integration??

    def toggle_breakpoint(self, f, l):
        ret = self.gdb_post({'type': 'toggle_breakpoint', 'file':f, 'line':l})
        if ret != None:
            self.update_bp_signs(ret['breakpoints'])

    def stop(self):
        ret = self.gdb_post({'type': 'stop'})

    def resume(self):
        ret = self.gdb_post({'type': 'resume'})

    def single_step(self):
        ret = self.gdb_post({'type': 'step'})

    def step_over(self):
        ret = self.gdb_post({'type': 'over'})

    def reset(self):
        ret = self.gdb_post({'type': 'reset'})

    def refresh_breakpoints(self):
        ret = self.gdb_post({'type': 'get_breakpoints'})
        if ret != None:
            self.update_bp_signs(ret['breakpoints'])

    def eval_word(self):
        # Get current word
        word = self.nvim.eval('expand(\'<cword>\')').strip('\n')
        ret = self.gdb_post({'type': 'eval_word', 'word': word})
        if ret != None:
            self.log(ret)

    def show_stack_trace(self):
        ret = self.gdb_post({'type': 'get_frames_string'})
        if ret != None:
            self.spawn_stacktrace_window(ret['frames_string'].split('\n'))

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
    print("here")
    ng.gdb_post({'type': 'over'})
    print('After post')
    ng.gdb_post({'type': 'over'})
    print('After post')
