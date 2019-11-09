import gdb
import re
import zmq
import msgpack
import threading

class GdbEvent():
    def __init__(self, cmd, callback=None, callback_data=None):
        self.cmd = cmd;
        self.callback = callback
        self.callback_data = callback_data
    def __call__(self):
        if self.callback != None:
            ret = gdb.execute(self.cmd, to_string=True)
            # Post the event
            if self.callback_data == 'eval_word_callback':
                # Filter out dollar sign
                a_ret = ret.split('\n')
                first_line_filt = re.findall(r'= (.*)', a_ret[0])[0]
                out_str = first_line_filt
                for i in range(1, len(a_ret)):
                    if a_ret[i] != '':
                        out_str += '\n' + a_ret[i]
                ret = out_str
            cbk_data = {'type': self.callback_data, 'data': str(ret)}
            self.callback(cbk_data)
        else:
            gdb.execute(self.cmd, to_string=True)

class NvGdb(object):
    def __init__(self):
        self.nvim_socket_connected = False
        self.pwd = gdb.execute('pwd', to_string=True)
        gdb.execute('set print pretty on', to_string=True)
        gdb.execute('set pagination off', to_string=True)
        self.pwd = self.pwd.split()[2][:-1]

    def get_breakpoints(self):
        bps = gdb.breakpoints()
        bps_list = []
        for b in bps:
            if b.enabled:
                bps_list.append(b.location)
        return bps_list

    def toggle_breakpoint(self, currentFile, currentLine):
        bps = gdb.breakpoints()
        currentFile = currentFile + ':' + str(currentLine)
        currentBp = None
        for b in bps:
            if currentFile == b.location:
                currentBp = b
        if currentBp != None:
            currentBp.enabled = not currentBp.enabled
        else:
            gdb.execute('b ' + currentLine, to_string=True)
        bps = self.get_breakpoints()
        return {'breakpoints': bps}

    def event_get_breakpoints(self):
        bps = self.get_breakpoints()
        return {'breakpoints': bps}

    def handle_event(self, msg):
        if msg['type'] == 'toggle_breakpoint':
            return self.toggle_breakpoint(msg['file'], msg['line'])
        elif msg['type'] == 'stop':
            # FIXME How to implement this?
            gdb.post_event(GdbEvent('c'))
            return {'status': True}
        elif msg['type'] == 'resume':
            gdb.post_event(GdbEvent('c'))
            return {'status': True}
        elif msg['type'] == 'step':
            gdb.post_event(GdbEvent('s'))
            return {'status': True}
        elif msg['type'] == 'over':
            gdb.post_event(GdbEvent('n'))
            return {'status': True}
        elif msg['type'] == 'reset':
            gdb.post_event(GdbEvent('r'))
            return {'status': True}
        elif msg['type'] == 'get_breakpoints':
            return self.event_get_breakpoints()
        elif msg['type'] == 'get_frames_string':
            ret = gdb.execute('bt', to_string=True)
            return {'frames_string': ret}
        elif msg['type'] == 'select_frame':
            gdb.execute('frame ' + str(msg['frame']), to_string=True)
            sal = gdb.selected_frame().find_sal()
            nvim_data = {}
            nvim_data['file'] = sal.symtab.fullname()
            nvim_data['line'] = sal.line
            return nvim_data
        elif msg['type'] == 'eval_word':
            gdb.post_event(GdbEvent('p ' + msg['word'], callback=self.nvim_post, callback_data='eval_word_callback'))
            return {'status': 'wait_for_callback'}
        else:
            return {'status': True}

    def serve(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:8765")
        while True:
            raw = socket.recv()
            msg = msgpack.unpackb(raw, raw=False)
            ret = self.handle_event(msg)
            socket.send(msgpack.packb(ret, use_bin_type=True))

    def start_server(self):
        self.t = threading.Thread(target=self.serve, daemon=True)
        self.t.start()

    def nvim_post(self, msg):
        if self.nvim_socket_connected is False:
            context = zmq.Context()
            self.socket = context.socket(zmq.REQ)
            self.socket.connect("tcp://localhost:5678")
            self.nvim_socket_connected = True
        msg_data = msgpack.packb(msg, use_bin_type=True)
        self.socket.send(msg_data)
        raw_resp = self.socket.recv()
        resp = msgpack.unpackb(raw_resp, raw=False)
        return resp

    def stop_event (self, event):
        sal = gdb.selected_frame().find_sal()
        nvim_data = {}
        nvim_data['type'] = 'bp_hit'
        nvim_data['file'] = sal.symtab.fullname()
        nvim_data['line'] = sal.line
        self.nvim_post(nvim_data)

# Initialize main class
nvg = NvGdb()
nvg.start_server()

gdb.events.stop.connect(nvg.stop_event)
