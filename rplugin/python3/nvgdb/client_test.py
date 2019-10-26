import time
import zmq
import msgpack

context = zmq.Context()

#  Socket to talk to server
print("Connecting to test server")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5678")

# Test 1
test_data = {}
test_data['type'] = 'bp_hit'
test_data['file'] = 'client_test.py'
test_data['line'] = 9

td = msgpack.packb(test_data, use_bin_type=True)
socket.send(td)

raw = socket.recv()
msg = msgpack.unpackb(raw, raw=False)
print(msg)

