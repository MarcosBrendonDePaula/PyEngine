import pygame
from typing import Tuple, Optional
from .ui_element import UIElement

class ProgressBar(UIElement):
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)
        
        # Progress value (0.0 to 1.0)
        self._progress = 0.0
        
        # Colors
        self.background_color = (50, 50, 50)  # Dark gray
        self.progress_color = (0, 255, 0)     # Green
        self.border_color = (100, 100, 100)   # Gray
        self.border_width = 1
        
    @property
    def progress(self) -> float:
        return self._progress
        
    @progress.setter
    def progress(self, value: float):
        """Set progress value, clamped between 0 and 1"""
        self._progress = max(0.0, min(1.0, value))
        
    def set_colors(self, progress_color: Tuple[int, int, int],
                   background_color: Optional[Tuple[int, int, int]] = None,
                   border_color: Optional[Tuple[int, int, int]] = None):
        """Set colors for the progress bar"""
        self.progress_color = progress_color
        if background_color is not None:
            self.background_color = background_color
        if border_color is not None:
            self.border_color = border_color
            
    def render(self, screen: pygame.Surface):
        """Render the progress bar"""
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        
        # Draw background
        pygame.draw.rect(screen, self.background_color,
                        (abs_x, abs_y, self.width, self.height))
        
        # Draw progress
        progress_width = int(self.width * self._progress)
        if progress_width > 0:
            pygame.draw.rect(screen, self.progress_color,
                           (abs_x, abs_y, progress_width, self.height))
        
        # Draw border
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(screen, self.border_color,
                           (abs_x, abs_y, self.width, self.height),
                           self.border_width)
