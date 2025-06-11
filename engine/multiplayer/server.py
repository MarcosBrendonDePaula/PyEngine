import socket
import threading
import json

class DedicatedServer:
    """Simple UDP-based server for syncing player actions."""

    def __init__(self, host: str = '0.0.0.0', port: int = 6000):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # map of player_id -> {"addr": (host, port), "host": bool}
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
        """Send a message to all connected clients except the excluded one."""
        data = json.dumps(message).encode('utf-8')
        for pid, info in list(self.clients.items()):
            if pid == exclude:
                continue
            self.sock.sendto(data, info["addr"])

    def _handle_packet(self, data: str, addr: tuple):
        try:
            msg = json.loads(data)
        except json.JSONDecodeError:
            return
        cmd = msg.get('cmd')
        pid = msg.get('player')
        if cmd == 'join':
            # store the new client's address and host flag
            self.clients[pid] = {"addr": addr, "host": msg.get("host")}
            # inform the newly connected client of all existing players
            for other_pid, info in self.clients.items():
                if other_pid == pid:
                    continue
                self.sock.sendto(
                    json.dumps({"cmd": "join", "player": other_pid, "host": info.get("host")}).encode("utf-8"),
                    addr,
                )
            # notify existing clients of the new player
            self.broadcast({"cmd": "join", "player": pid, "host": msg.get("host")}, exclude=pid)
        elif cmd == 'leave':
            if pid in self.clients:
                host_flag = self.clients[pid].get("host")
                del self.clients[pid]
            else:
                host_flag = msg.get("host")
            self.broadcast({"cmd": "leave", "player": pid, "host": host_flag})
        elif cmd == 'update':
            self.broadcast(msg, exclude=pid)

    def _recv_loop(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(2048)
                self._handle_packet(data.decode('utf-8'), addr)
            except OSError:
                break
