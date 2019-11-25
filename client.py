import socket
import threading
import configparser

from counterUtils import CounterUtils

config = configparser.ConfigParser()
config.read('conf.ini')

def heartbeat(server_address):
    connection.sendto(b'con-h 0x00', server_address)

    heartbeat_timer = threading.Timer(3, heartbeat, [server_address])
    heartbeat_timer.start()

# Create a UDP socket
connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
heartbeat_timer = None

server_address = ('localhost', 10000)

try:
    if config['client']['keep_alive'] == 'yes':
        heartbeat(server_address)

    while True:
        message = input('Type your message!')
        if message.startswith('com-0'):
            connection.sendto(message.encode(), server_address)
            if 'accept' not in message:
                data, _ = connection.recvfrom(4096)
                counter = CounterUtils.parse_counter(data.decode())
                print(data)
            continue

        connection.sendto(('msg-%i=%s' % (counter, message)).encode(), server_address)

        data, _ = connection.recvfrom(4096)
        counter = CounterUtils.parse_and_increment_counter(data.decode())

        if data.startswith(b'con-res'):
            print('Connection was reset')
            connection.sendto(b'con-res 0xFF', server_address)

        print(data)

finally:
    print('closing socket')
    connection.close()
