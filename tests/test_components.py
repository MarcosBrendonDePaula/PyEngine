import sys, os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import os
import pygame
import pytest
import threading

from engine.core.audio_manager import init_audio
from engine.core.save_manager import SaveManager
from engine.core.pathfinding import astar
from engine.core.components.particle_system import ParticleSystem
from engine.core.advanced_camera import AdvancedCamera
from engine.core.components.tilemap import TileMap
from engine.core.components.network_component import NetworkComponent
from engine.core.entity import Entity
from engine.core.scenes.base_scene import BaseScene

# Use headless mode for pygame
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
pygame.init()


pygame.display.set_mode((1, 1))
def test_audio_manager_init():
    init_audio()
    before = pygame.mixer.get_init()
    init_audio()
    after = pygame.mixer.get_init()
    assert before == after


def test_save_manager(tmp_path):
    path = tmp_path / "save.json"
    sm = SaveManager(str(path))
    data = {"score": 10}
    sm.save(data)
    loaded = sm.load()
    assert loaded == data


def test_astar_basic():
    grid = [
        [0, 0, 0],
        [1, 1, 0],
        [0, 0, 0],
    ]
    path = astar((0, 0), (2, 2), grid)
    assert path[0] == (0, 0)
    assert path[-1] == (2, 2)


class DummyInterface:
    def __init__(self):
        self.clock = pygame.time.Clock()


class DummyScene(BaseScene):
    def __init__(self):
        super().__init__(0)
        self.interface = DummyInterface()


def test_particle_system_lifecycle():
    entity = Entity()
    scene = DummyScene()
    entity.scene = scene
    ps = ParticleSystem(max_particles=1)
    entity.add_component(ps)
    ps.emit((0, 0), (1, 0), lifetime=0.05)
    for _ in range(5):
        scene.interface.clock.tick(60)
        entity.delta_time = 0.016  # 60 FPS
        entity.update()
    assert len(ps.particles) == 0


def test_advanced_camera_shake():
    cam = AdvancedCamera(100, 100)
    cam.start_shake(5, 0.1)
    offsets = []
    for _ in range(10):
        cam.update()
        offsets.append(cam.shake_offset.length())
    assert any(o > 0 for o in offsets)
    for _ in range(60):
        cam.update()
    assert cam.shake_offset.length() == 0


def test_tilemap_render(tmp_path):
    tileset = pygame.Surface((32, 32))
    tileset.fill((255, 0, 0))
    map_data = [[0]]
    file_path = tmp_path / "tiles.png"
    pygame.image.save(tileset, str(file_path))
    tm = TileMap(32, str(file_path), map_data)
    screen = pygame.Surface((32, 32))
    tm.render(screen)
    assert screen.get_at((16, 16)) == pygame.Color(255, 0, 0, 255)


def test_network_component_loopback():
    comp = NetworkComponent(port=0)
    comp.start()
    port = comp.socket.getsockname()[1]
    received = []
    done = threading.Event()
    def cb(data, addr):
        received.append(data)
        done.set()
    comp.recv_callback = cb
    comp.send("hello", ("127.0.0.1", port))
    for _ in range(50):
        pygame.time.delay(10)
        if done.is_set():
            break
    comp.stop()
    assert received == ["hello"]
