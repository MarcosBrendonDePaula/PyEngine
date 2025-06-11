import socket
import threading
import json

class DedicatedServer:
    """Simple UDP-based server for syncing player actions."""

    def __init__(self, host: str = '0.0.0.0', port: int = 6000):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clients = {}
        self.running = False
        self.thread = None

    def start(self):
        """Start listening for client packets."""
        self.sock.bind((self.host, self.port))
        self.running = True
        self.thread = threading.Thread(target=self._recv_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the server and close the socket."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.1)
        self.sock.close()

    def broadcast(self, message: dict, exclude: str | None = None):
        data = json.dumps(message).encode('utf-8')
        for pid, addr in list(self.clients.items()):
            if pid == exclude:
                continue
            self.sock.sendto(data, addr)

    def _handle_packet(self, data: str, addr: tuple):
        try:
            msg = json.loads(data)
        except json.JSONDecodeError:
            return
        cmd = msg.get('cmd')
        pid = msg.get('player')
        if cmd == 'join':
            self.clients[pid] = addr
            self.broadcast({'cmd': 'join', 'player': pid, 'host': msg.get('host')}, exclude=pid)
        elif cmd == 'leave':
            if pid in self.clients:
                del self.clients[pid]
            self.broadcast({'cmd': 'leave', 'player': pid, 'host': msg.get('host')})
        elif cmd == 'update':
            self.broadcast(msg, exclude=pid)

    def _recv_loop(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(2048)
                self._handle_packet(data.decode('utf-8'), addr)
            except OSError:
                break
