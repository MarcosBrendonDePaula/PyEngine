import argparse
import pygame
from engine import (create_engine, BaseScene, Entity, RectangleRenderer,
                    Physics, Collider, SyncComponent, Client)


class Player(Entity):
    def __init__(self, color, client):
        super().__init__(400, 300)
        self.renderer = self.add_component(RectangleRenderer(40, 40, color))
        self.physics = self.add_component(Physics(gravity=0))
        self.add_component(Collider(40, 40))
        self.add_component(SyncComponent(client))
        self.speed = 5

    def tick(self):
        super().tick()
        keys = pygame.key.get_pressed()
        vx = vy = 0
        if keys[pygame.K_a]:
            vx -= self.speed
        if keys[pygame.K_d]:
            vx += self.speed
        if keys[pygame.K_w]:
            vy -= self.speed
        if keys[pygame.K_s]:
            vy += self.speed
        self.physics.set_velocity(vx, vy)


class RemotePlayer(Entity):
    def __init__(self, color):
        super().__init__()
        self.renderer = self.add_component(RectangleRenderer(40, 40, color))


class NetworkScene(BaseScene):
    def __init__(self, client, color):
        super().__init__()
        self.client = client
        self.local_player = Player(color, client)
        self.remote_players = {}
        self.add_entity(self.local_player, "players")
        self.client.recv_callback = self.on_message

    def on_message(self, msg):
        pid = msg.get("player")
        if pid == self.client.player_id:
            return
        cmd = msg.get("cmd")
        if cmd == "join" and pid not in self.remote_players:
            remote = RemotePlayer((255, 0, 0))
            self.remote_players[pid] = remote
            self.add_entity(remote, "players")
        elif cmd == "leave" and pid in self.remote_players:
            self.remove_entity(self.remote_players.pop(pid), "players")
        elif cmd == "update":
            remote = self.remote_players.get(pid)
            if remote:
                data = msg.get("data", {})
                x = data.get("position.x")
                y = data.get("position.y")
                if x is not None:
                    remote.position.x = x
                if y is not None:
                    remote.position.y = y


def main(player_id: str, host: str, port: int):
    client = Client(player_id, host, port)
    engine = create_engine("Network Demo", 800, 600)
    scene = NetworkScene(client, (0, 255, 0))
    engine.set_scene("game", scene)
    engine.run()
    client.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("player_id")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=6000)
    args = parser.parse_args()
    main(args.player_id, args.host, args.port)
