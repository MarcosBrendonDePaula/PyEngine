import pygame
from typing import Tuple, Optional, Callable
from .ui_element import UIElement
from .label import Label

class Button(UIElement):
    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        super().__init__(x, y, width, height)
        
        # Button states
        self.hovered = False
        self.pressed = False
        
        # Colors for different states
        self.normal_color = (100, 100, 100)  # Gray
        self.hover_color = (120, 120, 120)   # Light gray
        self.pressed_color = (80, 80, 80)    # Dark gray
        self.background_color = self.normal_color
        
        # Create label for button text
        self.label = Label(0, 0, text)
        self.add_child(self.label)
        self._center_label()
        
        # Click handler
        self.on_click: Optional[Callable[[], None]] = None
        
    def _center_label(self):
        """Center the label within the button"""
        # Calculate centered position
        self.label.x = (self.width - self.label.width) // 2
        self.label.y = (self.height - self.label.height) // 2
        
    def set_text(self, text: str):
        """Update button text"""
        self.label.set_text(text)
        self._center_label()
        
    def set_colors(self, normal: Tuple[int, int, int],
                   hover: Tuple[int, int, int],
                   pressed: Tuple[int, int, int]):
        """Set button colors for different states"""
        self.normal_color = normal
        self.hover_color = hover
        self.pressed_color = pressed
        self.background_color = normal
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle button events"""
        if not self.enabled or not self.visible:
            return False
            
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Check if mouse is over button
        was_hovered = self.hovered
        self.hovered = self.contains_point(*mouse_pos)
        
        # Update background color based on state
        if self.pressed and self.hovered:
            self.background_color = self.pressed_color
        elif self.hovered:
            self.background_color = self.hover_color
        else:
            self.background_color = self.normal_color
            
        # Handle mouse events
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            if self.hovered:
                self.pressed = True
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.pressed
            self.pressed = False
            
            # If button was pressed and released while hovered, trigger click
            if was_pressed and self.hovered and self.on_click:
                self.on_click()
                return True
                
        return False
        
    def set_on_click(self, handler: Callable[[], None]):
        """Set click event handler"""
        self.on_click = handler

    def render(self, screen: pygame.Surface):
        """Render the button"""
        if not self.visible:
            return
            
        # Get absolute position for rendering
        abs_x, abs_y = self.get_absolute_position()
        
        # Draw button background
        pygame.draw.rect(screen, self.background_color,
                        (abs_x, abs_y, self.width, self.height))
        
        # Draw border if set
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(screen, self.border_color,
                           (abs_x, abs_y, self.width, self.height),
                           self.border_width)
        
        # Render label
        self.label.render(screen)
        
        # Debug: Draw rectangle around button
        pygame.draw.rect(screen, (255, 0, 0), 
                        (abs_x, abs_y, self.width, self.height), 1)
