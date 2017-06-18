import zmq
import random
import sys
import time
import json

port = "12000"

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:%s" % port)
while True:
    first_data_element = random.randrange(2,20)
    second_data_element = random.randrange(0,360)
    message = json.dumps({'First Data':first_data_element, 'Second Data':second_data_element})
    print(message)
    socket.send_string(message)
    time.sleep(0.5)