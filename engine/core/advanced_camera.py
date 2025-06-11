import random
import pygame
from .camera import Camera

class AdvancedCamera(Camera):
    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        self.shake_timer = 0.0
        self.shake_intensity = 0.0
        self.shake_offset = pygame.math.Vector2(0, 0)

    def start_shake(self, intensity: float, duration: float):
        self.shake_intensity = intensity
        self.shake_timer = duration

    def update(self):
        super().update()
        dt = 1 / 60
        if self.shake_timer > 0:
            self.shake_timer -= dt
            self.shake_offset.x = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_offset.y = random.uniform(-self.shake_intensity, self.shake_intensity)
        else:
            self.shake_offset.update(0, 0)

    def world_to_screen(self, world_pos):
        x, y = super().world_to_screen(world_pos)
        return x + self.shake_offset.x, y + self.shake_offset.y
