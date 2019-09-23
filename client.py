import socket

# Create a UDP socket
connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
counter = 0

server_address = ('localhost', 10000)

try:
    connection.sendto(('com-0 %s' % (socket.gethostbyname(socket.gethostname()))).encode(), server_address)
    data, _ = connection.recvfrom(4096)
    print(data)
    connection.sendto(b'com-0 accept', server_address)

    while True:
        message = input('Type your message!')
        connection.sendto(('msg-%i=%s' % (counter, message)).encode(), server_address)

        data, _ = connection.recvfrom(4096)
        counter += 2

        if data.startswith(b'res-'):
            print(data)

finally:
    print('closing socket')
    connection.close()
