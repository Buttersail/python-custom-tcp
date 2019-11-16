import configparser
import re
import socket
import time
import logging

from connectedClient import ConnectedClient, ConnectionState
from counterUtils import CounterUtils

config = configparser.ConfigParser()
config.read('conf.ini')

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='server.log',
                    filemode='w')
handshake_logger = logging.getLogger('handshake')

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
packages_received = (time.time(), 0)
connected_clients = {}

while True:
    print('\nwaiting to receive message')
    data, address = connection.recvfrom(4096)

    if address not in connected_clients:
        connected_clients[address] = ConnectedClient(address)

    if time.time() == packages_received[0]:
        if packages_received[1] < int(config['server']['pps']):
            packages_received = (packages_received[0], packages_received[1] + 1)
        else:
            print('Received too many messages, skipping')
            continue
    else:
        packages_received = (time.time(), 1)

    if connected_clients[address].connection_state == ConnectionState.INITIAL:
        if data.startswith(b'com-0'):
            print('received req from {}'.format(address))
            sent = connection.sendto(('com-0 accept %s' % (socket.gethostbyname(socket.gethostname()))).encode(),
                                     address)
            print('sent ack to {}'.format(address))
            connected_clients[address].connection_state = ConnectionState.HANDSHAKE_SERVER_ACK
            handshake_logger.info('Initial handshake from %s', [address])
        else:
            connection.sendto(b'con-err finish handshake first', address)
    elif connected_clients[address].connection_state == ConnectionState.HANDSHAKE_SERVER_ACK:
        if data == b'com-0 accept':
            print('received ack from {}'.format(address))
            connected_clients[address].reset_timer(connection_reset)
            connected_clients[address].connection_state = ConnectionState.VERIFIED
            handshake_logger.info('Handshake from %s finished', [address])
        else:
            connection.sendto(b'con-err finish handshake first', address)
    elif connected_clients[address].connection_state == ConnectionState.VERIFIED:
        connected_clients[address].reset_timer(connection_reset)

        if data.startswith(b'msg-'):
            print(data)
            clientCounter = CounterUtils.parse_and_increment_counter(data.decode())
            sent = connection.sendto(('res-%i=I am server' % (clientCounter)).encode(), address)
        elif data.startswith(b'con-res'):
            print('Received reset ack from Client')
        elif data.startswith(b'con-h'):
            print("Heartbeat *dunk*")
