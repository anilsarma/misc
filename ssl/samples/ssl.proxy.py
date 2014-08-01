#!/usr/bin/python 



# work in progress does not yet work.
import socket, ssl
import pprint
import sys
import threading


PORT = 10024

print "starting SSL(incoming) proxy server on %d" % (PORT)
bindsocket = socket.socket()
bindsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
bindsocket.bind(('', PORT))
bindsocket.listen(5)



def do_something(connstream, data):
    print "do_something:", data
    return False

def deal_with_client(connstream):
    data = connstream.read()
    while data:
        if not do_something(connstream, data):
            break
        data = connstream.read()


def process_incoming_ssl(input, output):
    data = input.recv(1024)
    try:
        while data:
            output.send(data);
            data = input.recv(1024)
    except:
        print "exception process_incoming_ssl:" , sys.exc_info()
        try:
            input.close()
        except:
            pass
        
def process_outgoing_ssl(input, output):
    data = input.recv(1024)
    try:
        while data:
            print data
            output.send(data);
            data = input.recv(1024)
    except:
        try:
            input.close()
        except:
            pass
        print "exception process_outgoing_ssl:" , sys.exc_info()

    

while True:
    newsocket, fromaddr = bindsocket.accept()
    connstream = None
    
    try:
        # we will verify both sides of the socket.
        connstream = ssl.wrap_socket(newsocket,
                                     server_side=True,
                                     certfile="server.crt",
                                     keyfile ="server.key",
                                     
                                     ca_certs="client.crt",
                                     cert_reqs=ssl.CERT_REQUIRED
                                     )
        
        # at this point the far end has been authenticated now we'll start a connection
        # to the next leg(un-encrypted)
        other_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        other_socket.connect(("localhost", 22))

        t1 = threading.Thread(target=process_incoming_ssl, args = (connstream, other_socket) );
        t1.daemon = True
        t1.start()

        t2 = threading.Thread(target=process_outgoing_ssl, args = (other_socket, connstream) );
        t2.daemon = True
        t2.start()
    
    except:
        print "exception:" , sys.exc_info()
        continue

    try:
        print repr(connstream.getpeername())
        print connstream.cipher()
        print "PEER CERT", pprint.pformat(connstream.getpeercert())
    
        #deal_with_client(connstream)
    finally:
        connstream.shutdown(socket.SHUT_RDWR)
        connstream.close()
        
