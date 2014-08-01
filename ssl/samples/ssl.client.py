#!/usr/bin/python

import socket, ssl, pprint

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Require a certificate from the server. We used a self-signed certificate
# so here ca_certs must be the server certificate itself.
ssl_sock = ssl.wrap_socket(s,
                           ca_certs="server.crt",
                           certfile="client.crt",
                           keyfile="client.key",
                           cert_reqs=ssl.CERT_REQUIRED)

ssl_sock.connect(('localhost', 10024))

print repr(ssl_sock.getpeername())
print ssl_sock.cipher()
print pprint.pformat(ssl_sock.getpeercert())

data = ssl_sock.recv(1024)
while data and len(data)>0:

	print "foo::", data
	data = ssl_sock.recv(1024)


ssl_sock.write("boo!")

if False: # from the Python 2.7.3 docs
    # Set a simple HTTP request -- use httplib in actual code.
    ssl_sock.write("""GET / HTTP/1.0\r
    Host: www.verisign.com\n\n""")

    # Read a chunk of data.  Will not necessarily
    # read all the data returned by the server.
    data = ssl_sock.recv()

    # note that closing the SSLSocket will also close the underlying socket
    ssl_sock.close()

