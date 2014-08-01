#!/usr/bin/python 



# work in progress 
# usefull to encrypt a connection over a public connection
# both ends of the connections is authenticated 
#
# to use this program, 2 set of certificates and keys are required
# 1 for the server side, and the other for the client side(currently takes only one client certificate)
#
#
#openssl genrsa -des3 -out server.orig.key 2048
#openssl rsa -in server.orig.key -out server.key
#openssl req -new -key server.key -out server.csr
#openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
#
#
import socket, ssl
import pprint
import sys, time
import threading
import getopt
from datetime import datetime


LISTEN_PORT = 10024
REMOTE_PORT = 10025
REMOTE_HOST="localhost"
REMOTE_CERT="client"
MY_CERT="server"
SERVER_MODE=True
VERBOSE=False
VERSION="0.1"

def usage():
	print sys.argv[0], " <options>"
	print "\t VERSION ", VERSION
	print "\t-client|-server -cert <my certificate prefix> -remote_cert <remote cert prefix>"
	print "\t--listen <port> --remote_host <hostname> --remote_port <port>" 
	print "\t--verbose"
	sys.exit(1)

try:
	opts, args = getopt.getopt(sys.argv[1:], "", ["help", "verbose", "client", 
			"server", "cert=", "remote_cert=", "listen=", "port=", "remote_host=", "host=", "remote_port="])
except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
   	usage()
        sys.exit(2)

output = None
verbose = False
for o, a in opts:
        if o == "--help":
            usage()
            sys.exit()
        if o == "--help":
            VERBOSE=True
        elif o == "--server":
	    SERVER_MODE = True 
        elif o == "--client":
	    SERVER_MODE = False 
        elif o == "--cert":
	    MY_CERT = a 
        elif o == "--remote_cert":
	    REMOTE_CERT = a 
        elif o in ("--listen", "--port"):
	    LISTEN_PORT = int(a) 
        elif o == "--remote_port":
	    REMOTE_PORT = int(a) 
        elif o in( "--remote_host", "--host"):
	    REMOTE_HOST = a 
        else:
            assert False, "unhandled option"


def hexdump(src, length=16):
	FILTER = ''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)])
	lines = []
	for c in xrange(0, len(src), length):
		chars = src[c:c+length]
		hex = ' '.join(["%02x" % ord(x) for x in chars])
		printable = ''.join(["%s" % ((ord(x) <= 127 and FILTER[ord(x)]) or '.') for x in chars])
		lines.append("%04x %-*s %s\n" % (c, length*3, hex, printable))
		return ''.join(lines)

def process_sockets(input, output):
    data = input.recv(1024)
    try:
        while data:
	    if VERBOSE:
	    	print datetime.now().strftime("%H:%M:%S.%f"), "\n", hexdump(src=data)
            output.send(data)
            data = input.recv(1024)
    except:
        print "exception process_incoming_ssl:" , sys.exc_info()
        try:
            output.shutdown(socket.SHUT_RDWR)
            output.close()
        except:
            pass
        try:
            input.shutdown(socket.SHUT_RDWR)
            input.close()
        except:
            pass
        
    

print sys.argv[0], " VERSION ", VERSION
print "Running in Server Mode", (SERVER_MODE)
print "starting SSL(incoming) proxy server SERVER PORT %d, Remote Port %d" % (LISTEN_PORT, REMOTE_PORT)
serversocket = socket.socket
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversocket.bind(('', LISTEN_PORT))
serversocket.listen(5)

while True:
    newsocket, fromaddr = serversocket.accept()
    
    try:
        # we will verify both sides of the socket.
	if SERVER_MODE:
		print "securing server connection .. "
        	newsocket = ssl.wrap_socket(newsocket,
                                     server_side=True,
                                     certfile=MY_CERT + ".crt",
                                     keyfile =MY_CERT + ".key",
                                     
                                     ca_certs=REMOTE_CERT+".crt",
                                     cert_reqs=ssl.CERT_REQUIRED
                                     )
        
        # at this point the far end has been authenticated now we'll start a connection
        # to the next leg(un-encrypted)
        other_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        other_socket.connect((REMOTE_HOST, REMOTE_PORT))
	if not SERVER_MODE:
		print "securing client connection .. "
        	other_socket = ssl.wrap_socket(other_socket,
                                     server_side=False,
                                     certfile=MY_CERT + ".crt",
                                     keyfile =MY_CERT + ".key",
                                     
                                     ca_certs=REMOTE_CERT+".crt",
                                     cert_reqs=ssl.CERT_REQUIRED
                                     )
        


        t1 = threading.Thread(target=process_sockets, args = (newsocket, other_socket) );
        t1.daemon = True
        t1.start()

        t2 = threading.Thread(target=process_sockets, args = (other_socket, newsocket) );
        t2.daemon = True
        t2.start()
    
    except:
        print "exception:" , sys.exc_info()
	try:
        	newsocket.shutdown(socket.SHUT_RDWR)
        	newsocket.close()
	except:
		pass
	try:
        	other_socket.shutdown(socket.SHUT_RDWR)
        	other_socket.close()
	except:
		pass
        continue

