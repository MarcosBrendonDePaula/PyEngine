import pygame
from typing import Tuple
from engine.core.components.ui.button import Button
from engine.core.components.ui.label import Label

class ButtonWrapper(Button):
    """A wrapper for Button that can handle camera_offset parameter"""
    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        super().__init__(x, y, width, height, text)
    
    def render(self, screen: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)):
        """Render the button, ignoring camera_offset"""
        super().render(screen)

class LabelWrapper(Label):
    """A wrapper for Label that can handle camera_offset parameter"""
    def __init__(self, x: int, y: int, text: str, font_size: int = 24):
        super().__init__(x, y, text, font_size)
    
    def render(self, screen: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)):
        """Render the label, ignoring camera_offset"""
        super().render(screen)
