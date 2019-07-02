import socket, threading, time
import utilities
from constants import *

class PacketManager:
    def __init__ (self, target):
        self._target = target
        self._thread = None
        self._is_running = False
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind(utilities.HELPER)

    def _refuse (self):
        data, address = self._target.recvfrom(DATA_LENGTH)
        self._is_running = False

    def _delay (self, t):
        data, address = self._target.recvfrom(DATA_LENGTH)
        time.sleep(t)
        self._socket.sendto(data, (utilities.get_ip(), self._target.getsockname()[1]))
        self._is_running = False

    def refuse (self):
        if not self._is_running:
            self._is_running = True
            self._thread = threading.Thread(target = self._refuse)
            self._thread.start()

    def delay (self, t):
        if not self._is_running:
            self._is_running = True
            self._thread = threading.Thread(target = lambda: self._delay(t))
            self._thread.start()

    def close (self):
        self._socket.close()
