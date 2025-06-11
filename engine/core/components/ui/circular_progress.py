import pygame
import math
from typing import Tuple
from .ui_element import UIElement

class CircularProgress(UIElement):
    """Circular progress indicator."""

    def __init__(self, x: int, y: int, radius: int, thickness: int = 6):
        super().__init__(x, y, radius * 2, radius * 2)
        self.radius = radius
        self.thickness = thickness
        self._progress = 0.0

        self.track_color = (50, 50, 50)    # Dark gray
        self.progress_color = (0, 255, 0)  # Green

    @property
    def progress(self) -> float:
        return self._progress

    @progress.setter
    def progress(self, value: float):
        self._progress = max(0.0, min(1.0, value))

    def render(self, screen: pygame.Surface):
        if not self.visible:
            return

        abs_x, abs_y = self.get_absolute_position()
        center = (abs_x + self.radius, abs_y + self.radius)
        rect = pygame.Rect(abs_x, abs_y, self.radius * 2, self.radius * 2)

        # Draw track circle
        pygame.draw.circle(screen, self.track_color, center, self.radius, self.thickness)

        # Draw progress arc
        if self._progress > 0:
            start_angle = -math.pi / 2
            end_angle = start_angle + 2 * math.pi * self._progress
            if self._progress >= 1.0:
                pygame.draw.circle(screen, self.progress_color, center, self.radius, self.thickness)
            else:
                pygame.draw.arc(screen, self.progress_color, rect, start_angle, end_angle, self.thickness)
