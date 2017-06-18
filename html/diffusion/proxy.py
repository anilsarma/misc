import zmq

def run():
    context = zmq.Context()
    frontend = context.socket(zmq.ROUTER)
    frontend.bind('tcp://*:10000')

    backend = context.socket(zmq.DEALER)
#    backend.bind('ipc://backend')

    zmq.proxy(frontend, backend)

    
if __name__ == '__main__':
    run()