import gdb
import re
import zmq
import msgpack
import threading


class NvGdb(object):
    def __init__(self):
        self.nvim_socket_connected = False
        self.pwd = gdb.execute('pwd', to_string=True)
        self.pwd = self.pwd.split()[2][:-1]

    def toggle_breakpoint(self, currentFile, currentLine):
        bps = gdb.breakpoints()
        currentFile = currentFile.replace(self.pwd+'/', '')
        currentFile = currentFile + ':' + str(currentLine)
        print(currentFile)
        # FIXME implement toggling of breakpoint.. cont here
        for b in bps:
            print(b.location)
        return {'active': True}

    def handle_event(self, msg):
        if msg['type'] == 'toggle_breakpoint':
            return self.toggle_breakpoint(msg['file'], msg['line'])
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
