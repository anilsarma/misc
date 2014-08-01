import socket, ssl
import pprint
import sys

bindsocket = socket.socket()
bindsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
bindsocket.bind(('', 10024))
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

while True:
    newsocket, fromaddr = bindsocket.accept()
    connstream = None

    try:
        connstream = ssl.wrap_socket(newsocket,
                                 server_side=True,
                                 certfile="server.crt",
                                 keyfile="server.key",

                                 ca_certs="client.crt",
                                 cert_reqs=ssl.CERT_REQUIRED
                                        )
    except:
            print "exception:" , sys.exc_info()
            continue
    try:
        print repr(connstream.getpeername())
        print connstream.cipher()
        print "PEER CERT", pprint.pformat(connstream.getpeercert())

        deal_with_client(connstream)
    finally:
        connstream.shutdown(socket.SHUT_RDWR)
        connstream.close()
