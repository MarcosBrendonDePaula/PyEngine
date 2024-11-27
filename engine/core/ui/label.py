import pygame
from typing import Tuple, Optional
from .ui_element import UIElement

class Label(UIElement):
    def __init__(self, x: int, y: int, text: str, font_size: int = 24):
        # Initialize pygame font if not already initialized
        if not pygame.font.get_init():
            pygame.font.init()
            
        self.font = pygame.font.Font(None, font_size)
        self.text = text
        self.text_color = (255, 255, 255)  # Default white
        self.padding = 5  # Padding around text
        
        # Calculate size based on text
        text_surface = self.font.render(text, True, self.text_color)
        width = text_surface.get_width() + (self.padding * 2)  # Add padding on both sides
        height = text_surface.get_height() + (self.padding * 2)
        
        super().__init__(x, y, width, height)
        
    def set_text(self, text: str):
        """Update the label's text"""
        self.text = text
        # Recalculate size
        text_surface = self.font.render(text, True, self.text_color)
        self.width = text_surface.get_width() + (self.padding * 2)
        self.height = text_surface.get_height() + (self.padding * 2)
        
    def set_text_color(self, color: Tuple[int, int, int]):
        """Set the text color"""
        self.text_color = color
        
    def render(self, screen: pygame.Surface):
        """Render the label"""
        if not self.visible:
            return
            
        # Get absolute position for rendering
        abs_x, abs_y = self.get_absolute_position()
        
        # Draw background if set
        if self.background_color is not None:
            if len(self.background_color) == 4:  # With alpha
                surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                surface.fill(self.background_color)
                screen.blit(surface, (abs_x, abs_y))
            else:  # Without alpha
                pygame.draw.rect(screen, self.background_color,
                               (abs_x, abs_y, self.width, self.height))
        
        # Draw border if set
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(screen, self.border_color,
                           (abs_x, abs_y, self.width, self.height),
                           self.border_width)
        
        # Then render the text
        try:
            text_surface = self.font.render(self.text, True, self.text_color)
            
            # Position text with padding
            text_x = abs_x + self.padding
            text_y = abs_y + self.padding
            
            screen.blit(text_surface, (text_x, text_y))
        except pygame.error as e:
            print(f"Error rendering text: {e}")
            print(f"Text: {self.text}")
            print(f"Color: {self.text_color}")
