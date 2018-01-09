import socket
import struct
from threading import Thread
from time import sleep

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

    def connect(self):
        m_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.tx_timeout_sec is not None:
            timeout_sec = int(self.tx_timeout_sec)
            timeout_usec = int((self.tx_timeout_sec - timeout_sec) * 1e6)
            timeval = struct.pack('ll', timeout_sec, timeout_usec)
            m_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDTIMEO, timeval)

        if self.rx_timeout_sec is not None:
            timeout_sec = int(self.rx_timeout_sec)
            timeout_usec = int((self.rx_timeout_sec - timeout_sec) * 1e6)
            timeval = struct.pack('ll', timeout_sec, timeout_usec)
            m_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeval)

        m_socket.connect((self.ip_address, self.port))
        self.socket = m_socket

        thread = Thread(target=self.background_thread_function)
        thread.start()

    def background_thread_function(self):
        while True:
            try:
                rxdata = self.socket.recv(RX_BUFFER_SIZE)
                if not rxdata:
                    break
            except Exception as e:
                DEBUG_LOG(e)
                break
        self.socket.close()
        self.socket = None

    def send(self, data):
        while True:
            try:
                if not self.socket:
                    self.connect()

                self.socket.send(data)
                break
            except OSError as e:
                DEBUG_LOG(e)
                sleep(1)
