import pygame
import random
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.particle_system import ParticleSystem
from engine.core.components.debug_info import DebugInfoComponent
from engine.core.components.ui.slider import Slider
from engine import Engine

class DebugInfo(Entity):
    def __init__(self):
        super().__init__(0, 0)
        self.add_component(DebugInfoComponent())

class WaterParticleScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.background_color = (10, 10, 30)
        self.emitter = Entity(400, 50)
        self.particle_system = self.emitter.add_component(ParticleSystem(max_particles=10000))
        self.add_entity(self.emitter)
        self.gravity = pygame.math.Vector2(0, 200)
        self.spawn_rate = 20
        self.spawn_spread = 24
        self.add_entity(DebugInfo())
        
        slider = Slider(100,0, 100, 50,)
        slider.max_value = 250
        slider.min_value = 10
        slider.on_value_changed = self.ChangeFps

        self.add_entity(slider)

    def ChangeFps(self, value):
        Engine.ENGINE_INSTANCE.interface.set_fps(int(value))
        print(value)
        
        pass

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEMOTION:
            self.emitter.position.x = event.pos[0]

    def update(self, delta):
        super().update(delta)
        if not self._is_loaded:
            return
        dt = self.interface.clock.get_time() / 1000.0
        for _ in range(self.spawn_rate):
            offset_x = random.uniform(-self.spawn_spread/2, self.spawn_spread/2)
            pos = (self.emitter.position.x + offset_x, self.emitter.position.y)
            vel = pygame.math.Vector2(random.uniform(-30, 30), random.uniform(0, 50))
            self.particle_system.emit(pos, vel, color=(0, 150, 255), lifetime=5.0, radius=2)

        floor_y = self.interface.size[1] - 10
        for p in self.particle_system.particles:
            p.velocity += self.gravity * dt
            if p.position.y >= floor_y:
                p.position.y = floor_y
                p.velocity.y *= -0.3

    def render(self, screen: pygame.Surface):
        screen.fill(self.background_color)
        super().render(screen)
