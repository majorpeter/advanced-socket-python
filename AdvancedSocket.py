import socket
import struct
from threading import Thread
from time import sleep

RX_BUFFER_SIZE = 4096


def DEBUG_LOG(message):
    print(message)


class AdvancedSocket():
    def __init__(self, ip_address, port,
                 max_reconnects=None, reconnect_delay_sec=2,
                 rx_timeout_sec=None, tx_timeout_sec=1.5,
                 on_receive_callback=None):
        self.ip_address = ip_address
        self.port = port
        self.max_reconnects = max_reconnects
        self.reconnect_delay_sec = reconnect_delay_sec
        self.rx_timeout_sec = rx_timeout_sec
        self.tx_timeout_sec = tx_timeout_sec
        self.on_receive_callback = on_receive_callback
        self.socket = None

    def is_connected(self):
        return self.socket is not None

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
                if self.on_receive_callback is not None:
                    self.on_receive_callback(rxdata)
            except Exception as e:
                DEBUG_LOG('recv exception: ' + str(e))
                break
        self.socket.close()
        self.socket = None

    def send(self, data):
        max_reconnects = self.max_reconnects
        while True:
            try:
                if self.socket is None:
                    self.connect()

                self.socket.send(data)
                break
            except OSError as e:
                DEBUG_LOG('send os error: ' + str(e))
                if self.socket is not None:
                    self.socket.close()
                    self.socket = None

                if max_reconnects is not None:
                    if max_reconnects == 0:
                        DEBUG_LOG('Max reconnects reached (%d)' % self.max_reconnects)
                        return False
                    max_reconnects -= 1

                sleep(self.reconnect_delay_sec)
        return True
