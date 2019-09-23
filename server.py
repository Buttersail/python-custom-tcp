import socket
import re

# Create a UDP socket
connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print('starting up on {} port {}'.format(*server_address))
connection.bind(server_address)

while True:
    print('\nwaiting to receive message')
    data, address = connection.recvfrom(4096)

    if data == b'com-0 accept':
        print('received ack from {}'.format(address))
    elif data.startswith(b'com-0'):
        print('received req from {}'.format(address))
        sent = connection.sendto(('com-0 accept %s' % (socket.gethostbyname(socket.gethostname()))).encode(), address)
        print('sent ack to {}'.format(address))
    elif data.startswith(b'msg-'):
        clientCounter = int(re.compile(r"msg-(\d+).*").match(data.decode()).group(1)) + 1
        sent = connection.sendto(('res-%i=I am server' % (clientCounter)).encode(), address)
