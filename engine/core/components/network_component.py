import socket
import threading
from ..component import Component

class NetworkComponent(Component):
    def __init__(self, host: str = 'localhost', port: int = 5000):
        super().__init__()
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_callback = None
        self._running = False
        self._thread = None

    def start(self):
        self.socket.bind((self.host, self.port))
        self._running = True
        self._thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=0.1)
        self.socket.close()

    def send(self, data: str, address: tuple):
        self.socket.sendto(data.encode('utf-8'), address)

    def _recv_loop(self):
        while self._running:
            try:
                data, addr = self.socket.recvfrom(1024)
                if self.recv_callback:
                    self.recv_callback(data.decode('utf-8'), addr)
            except OSError:
                break
