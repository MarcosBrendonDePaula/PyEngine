import pygame
from ..component import Component
from typing import Tuple

class RectangleRenderer(Component):
    def __init__(self, width: float, height: float, color: Tuple[int, int, int]):
        super().__init__()
        self.width = width
        self.height = height
        self.color = color
        self.offset = pygame.math.Vector2(0, 0)

    def render(self, screen: pygame.Surface, camera_offset=(0, 0)):
        if not self.enabled or not self.entity:
            return

        render_pos = (
            self.entity.position.x - camera_offset[0] + self.offset.x,
            self.entity.position.y - camera_offset[1] + self.offset.y
        )

        pygame.draw.rect(
            screen,
            self.color,
            (render_pos[0] - self.width/2,
             render_pos[1] - self.height/2,
             self.width,
             self.height)
        )

    def set_color(self, color: Tuple[int, int, int]):
        """Change the rectangle's color"""
        self.color = color

    def set_size(self, width: float, height: float):
        """Change the rectangle's size"""
        self.width = width
        self.height = height

    def set_offset(self, x: float, y: float):
        """Set rendering offset from entity position"""
        self.offset.x = x
        self.offset.y = y
