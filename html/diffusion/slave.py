import zmq
from multiprocessing import Process
import json


def slave():
    context = zmq.Context()
    worker = context.socket(zmq.DEALER)
#    worker.connect('ipc://backend')
    print 'Worker started'

    while True:
        ident, data = worker.recv_multipart()
        data = json.loads(data)
        # get the id of the pixel
        idx = data["idx"]
        arr = data["data"]
        # run the 'computation' on the data
        res = run_computation(arr)
        out = {"idx": idx, "result": res}

        worker.send_multipart([ident, json.dumps(out)])

def run_computation(data):
    dx = 0.1
    dy = 0.1
    nu = 10.00
    sigma = 0.25
    dt = sigma * dx * dy / nu
    res = data[1][1] + \
          (nu * dt / dx ** 2) * (data[1][2] - 2 * data[1][1] + data[1][0]) + \
          (nu * dt / dy ** 2) * (data[0][1] - 2 * data[1][1] + data[2][1])
    return res

if __name__ == "__main__":
    NUM_SLAVES = 6
    for i in xrange(NUM_SLAVES):
        p = Process(target=slave).start()
