import socket
import struct
from threading import Thread


RX_BUFFER_SIZE = 4096


def DEBUG_LOG(message):
    print(message)


class AdvancedSocket():
    def __init__(self, ip_address, port, max_reconnects=None, rx_timeout_sec=None, tx_timeout_sec=1.5):
        self.ip_address = ip_address
        self.port = port
        self.max_reconnects = max_reconnects
        self.rx_timeout_sec = rx_timeout_sec
        self.tx_timeout_sec = tx_timeout_sec
        self.socket = None

        self.connect()

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.tx_timeout_sec is not None:
            timeout_sec = int(self.tx_timeout_sec)
            timeout_usec = int((self.tx_timeout_sec - timeout_sec) * 1e6)
            timeval = struct.pack('ll', timeout_sec, timeout_usec)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDTIMEO, timeval)

        if self.rx_timeout_sec is not None:
            timeout_sec = int(self.rx_timeout_sec)
            timeout_usec = int((self.rx_timeout_sec - timeout_sec) * 1e6)
            timeval = struct.pack('ll', timeout_sec, timeout_usec)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeval)

        self.socket.connect((self.ip_address, self.port))
        thread = Thread(target=self.background_thread_function)
        thread.start()

    def background_thread_function(self):
        while True:
            try:
                rxdata = self.socket.recv(RX_BUFFER_SIZE)
                if not rxdata:
                    break
            except Exception as e:
                print(e)
                break
        self.socket.close()

    def send(self, data):
        self.socket.send(data)
