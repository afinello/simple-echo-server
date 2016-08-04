import socket
import time

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 8000)
print 'connecting to %s port %s' % server_address
sock.connect(server_address)

for x in range(0, 2):
    try:
        # Send data
        sock.sendall('hello')
        time.sleep(1)

        response = sock.recv(16)
        print 'received "%s"' % response

    except Exception, e:
        print 'error'

print 'closing socket'
sock.close()
