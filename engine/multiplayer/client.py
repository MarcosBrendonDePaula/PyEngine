import socket
import threading
import json

class Client:
    """Client for communicating with the DedicatedServer."""

    def __init__(self, player_id: str, host: str = 'localhost', port: int = 6000, *, is_host: bool = False):
        self.server = (host, port)
        self.player_id = player_id
        self.is_host = is_host
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_callback = None
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._recv_loop, daemon=True)
        self.thread.start()
        self.send({'cmd': 'join', 'player': self.player_id, 'host': self.is_host})

    def stop(self):
        self.send({'cmd': 'leave', 'player': self.player_id, 'host': self.is_host})
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.1)
        self.sock.close()

    def send_update(self, data: dict):
        self.send({'cmd': 'update', 'player': self.player_id, 'data': data, 'host': self.is_host})

    def send(self, message: dict):
        self.sock.sendto(json.dumps(message).encode('utf-8'), self.server)

    def _recv_loop(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(2048)
                if self.recv_callback:
                    self.recv_callback(json.loads(data.decode('utf-8')))
            except OSError:
                break
