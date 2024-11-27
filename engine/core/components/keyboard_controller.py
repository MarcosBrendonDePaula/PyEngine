import pygame
from ..component import Component

class KeyboardController(Component):
    def __init__(self, speed: float = 5.0):
        super().__init__()
        self.speed = speed
        self.bindings = {
            pygame.K_LEFT: (-1, 0),
            pygame.K_RIGHT: (1, 0),
            pygame.K_UP: (0, -1),
            pygame.K_DOWN: (0, 1)
        }

    def tick(self):
        if not self.enabled or not self.entity:
            return

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        for key, (dir_x, dir_y) in self.bindings.items():
            if keys[key]:
                dx += dir_x
                dy += dir_y

        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.707  # 1/√2
            dy *= 0.707

        # Apply movement
        self.entity.move(dx * self.speed, dy * self.speed)

    def set_binding(self, key: int, direction: tuple):
        """Set a custom key binding"""
        self.bindings[key] = direction

    def clear_bindings(self):
        """Clear all key bindings"""
        self.bindings.clear()
