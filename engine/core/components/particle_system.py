import pygame
import random
from ..component import Component

class Particle:
    def __init__(self, position, velocity, color, lifetime, radius=2):
        self.position = pygame.math.Vector2(position)
        self.velocity = pygame.math.Vector2(velocity)
        self.color = color
        self.lifetime = lifetime
        self.age = 0.0
        self.radius = radius

class ParticleSystem(Component):
    def __init__(self, max_particles=100):
        super().__init__()
        self.max_particles = max_particles
        self.particles = []

    def emit(self, position, velocity, color=(255, 255, 255), lifetime=1.0, radius=2):
        if len(self.particles) < self.max_particles:
            self.particles.append(Particle(position, velocity, color, lifetime, radius))

    def update(self):
        if not self.enabled:
            return
        dt = self.entity.delta_time if self.entity and hasattr(self.entity, 'delta_time') else 1/60
        for p in self.particles[:]:
            p.position += p.velocity * dt
            p.age += dt
            if p.age >= p.lifetime:
                self.particles.remove(p)

    def render(self, screen: pygame.Surface, offset=(0,0)):
        for p in self.particles:
            pos = (int(p.position.x - offset[0]), int(p.position.y - offset[1]))
            pygame.draw.circle(screen, p.color, pos, p.radius)
