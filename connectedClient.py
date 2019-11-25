import threading
from enum import Enum

class ConnectionState(Enum):
    INITIAL = 1
    HANDSHAKE_SERVER_ACK = 2
    VERIFIED = 3

class ConnectedClient:
    address = None
    timer = None
    connection_state = ConnectionState.INITIAL

    def __init__(self, address):
        self.address = address

    def connection_reset_timer(self, connection_reset):
        if self.timer is not None:
            self.timer.cancel()
        self.timer = threading.Timer(4, connection_reset, [self.address])
        self.timer.start()

