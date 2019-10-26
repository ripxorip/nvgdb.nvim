import gdb
import re
import zmq
import msgpack

def stop_event (event):
    sal = gdb.selected_frame().find_sal()

    bp = {}
    bp['type'] = 'bp_hit'
    bp['file'] = sal.symtab.fullname()
    bp['line'] = sal.line

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5678")

    bp_data = msgpack.packb(bp, use_bin_type=True)
    socket.send(bp_data)
    raw_resp = socket.recv()

    msg = msgpack.unpackb(raw_resp, raw=False)
    print(msg)

gdb.events.stop.connect(stop_event)
