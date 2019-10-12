import socket
import re
import threading
import time
import configparser

config = configparser.ConfigParser()
config.read('conf.ini')

def connection_reset(address):
    print('Resetting connection')
    print(address)
    connection.sendto(b'con-res 0xFE', address)

# Create a UDP socket
connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print('starting up on {} port {}'.format(*server_address))
connection.bind(server_address)
reset_timers = {}
packages_received = (time.time(), 0)

while True:
    print('\nwaiting to receive message')
    data, address = connection.recvfrom(4096)

    if time.time() == packages_received[0]:
        if packages_received[1] < int(config['server']['pps']):
            packages_received[1] += 1
        else:
            print('Received too many messages, skipping')
            continue
    else:
        packages_received = (time.time(), 1)

    if data == b'com-0 accept':
        reset_timers[address] = threading.Timer(4, connection_reset, [address])
        reset_timers[address].start()
        print('received ack from {}'.format(address))
    elif data.startswith(b'com-0'):
        print('received req from {}'.format(address))
        sent = connection.sendto(('com-0 accept %s' % (socket.gethostbyname(socket.gethostname()))).encode(), address)
        print('sent ack to {}'.format(address))
    elif data.startswith(b'msg-'):
        reset_timers[address].cancel()
        clientCounter = int(re.compile(r"msg-(\d+).*").match(data.decode()).group(1)) + 1
        sent = connection.sendto(('res-%i=I am server' % (clientCounter)).encode(), address)
        reset_timers[address] = threading.Timer(4, connection_reset, [address])
        reset_timers[address].start()
    elif data.startswith(b'con-res'):
        print('Received reset ack from Client')
        reset_timers[address] = threading.Timer(4, connection_reset, [address])
        reset_timers[address].start()
    elif data.startswith(b'con-h'):
        reset_timers[address].cancel()
        reset_timers[address] = threading.Timer(4, connection_reset, [address])
        reset_timers[address].start()



