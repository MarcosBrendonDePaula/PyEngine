import pygame
from engine.core.scenes.base_scene import BaseScene

class LiquidDemoScene(BaseScene):
    def __init__(self, width=200, height=150, scale=4):
        super().__init__()
        self.grid_width = width
        self.grid_height = height
        self.scale = scale
        self.damping = 0.99
        # Height buffers
        self.current = [[0.0 for _ in range(height)] for _ in range(width)]
        self.previous = [[0.0 for _ in range(height)] for _ in range(width)]
        self.surface = pygame.Surface((width, height))

    def disturb(self, x, y, magnitude=100.0):
        if 1 <= x < self.grid_width-1 and 1 <= y < self.grid_height-1:
            self.previous[x][y] = magnitude

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            gx = event.pos[0] // self.scale
            gy = event.pos[1] // self.scale
            self.disturb(gx, gy)

    def update(self, delta_time: float):
        super().update(delta_time)
        if not self._is_loaded:
            return
        for x in range(1, self.grid_width-1):
            for y in range(1, self.grid_height-1):
                val = (
                    self.previous[x-1][y] +
                    self.previous[x+1][y] +
                    self.previous[x][y-1] +
                    self.previous[x][y+1]
                ) / 2 - self.current[x][y]
                val *= self.damping
                self.current[x][y] = val
        # Swap buffers
        self.current, self.previous = self.previous, self.current

        # Update surface pixels
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                c = 127 + int(self.current[x][y])
                c = max(0, min(255, c))
                self.surface.set_at((x, y), (0, 0, c))

    def render(self, screen: pygame.Surface):
        scaled = pygame.transform.scale(
            self.surface,
            (self.grid_width * self.scale, self.grid_height * self.scale)
        )
        screen.blit(scaled, (0, 0))
