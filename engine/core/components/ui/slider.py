import pygame
from typing import Tuple, Optional, Callable
from .ui_element import UIElement

class Slider(UIElement):
    def __init__(self, x: int, y: int, width: int, height: int, 
                 min_value: float = 0.0, max_value: float = 1.0, 
                 initial_value: float = 0.0, vertical: bool = False):
        super().__init__(x, y, width, height)
        
        # Value properties
        self.min_value = min_value
        self.max_value = max_value
        self._value = min_value
        self.vertical = vertical
        
        # Handle properties
        self.handle_width = 20
        self.handle_height = height if vertical else height
        self._dragging = False
        self._handle_offset = 0
        
        # Style properties
        self.track_color = (200, 200, 200)  # Light gray
        self.handle_color = (100, 100, 100)  # Dark gray
        self.active_handle_color = (80, 80, 80)  # Darker gray when dragging
        
        # Callback
        self.on_value_changed: Optional[Callable[[float], None]] = None
        
        # Set initial value
        self.value = initial_value
    
    @property
    def value(self) -> float:
        """Get current value"""
        return self._value
        
    @value.setter
    def value(self, new_value: float):
        """Set current value, clamped to min/max range"""
        old_value = self._value
        self._value = max(self.min_value, min(self.max_value, new_value))
        
        if self._value != old_value and self.on_value_changed:
            self.on_value_changed(self._value)
    
    def _get_handle_position(self) -> Tuple[int, int]:
        """Get handle position based on current value"""
        value_range = self.max_value - self.min_value
        value_percent = (self.value - self.min_value) / value_range if value_range != 0 else 0
        
        if self.vertical:
            y = int(value_percent * (self.height - self.handle_height))
            return (0, y)
        else:
            x = int(value_percent * (self.width - self.handle_width))
            return (x, 0)
    
    def _value_from_position(self, pos: Tuple[int, int]) -> float:
        """Convert screen position to slider value"""
        abs_x, abs_y = self.get_absolute_position()
        x, y = pos[0] - abs_x, pos[1] - abs_y
        
        if self.vertical:
            track_length = self.height - self.handle_height
            pos = max(0, min(track_length, y))
            value_percent = pos / track_length if track_length != 0 else 0
        else:
            track_length = self.width - self.handle_width
            pos = max(0, min(track_length, x))
            value_percent = pos / track_length if track_length != 0 else 0
            
        return self.min_value + (self.max_value - self.min_value) * value_percent
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events for dragging"""
        if not self.enabled or not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if click is on handle
            handle_x, handle_y = self._get_handle_position()
            abs_x, abs_y = self.get_absolute_position()
            mouse_x, mouse_y = event.pos
            rel_x, rel_y = mouse_x - abs_x, mouse_y - abs_y
            
            handle_rect = pygame.Rect(
                handle_x, handle_y, 
                self.handle_width, self.handle_height
            )
            
            if handle_rect.collidepoint(rel_x, rel_y):
                self._dragging = True
                # Store offset from handle position to mouse position
                self._handle_offset = (rel_x - handle_x) if not self.vertical else (rel_y - handle_y)
                return True
                
            # Click on track - move handle to that position
            if self.contains_point(mouse_x, mouse_y):
                self.value = self._value_from_position((mouse_x, mouse_y))
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._dragging = False
            
        elif event.type == pygame.MOUSEMOTION and self._dragging:
            mouse_x, mouse_y = event.pos
            if self.vertical:
                self.value = self._value_from_position((mouse_x, mouse_y - self._handle_offset))
            else:
                self.value = self._value_from_position((mouse_x - self._handle_offset, mouse_y))
            return True
            
        return False
    
    def render(self, screen: pygame.Surface, camera_offset):
        """Render slider track and handle"""
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        
        # Draw track
        pygame.draw.rect(screen, self.track_color,
                        (abs_x, abs_y, self.width, self.height))
        
        # Draw handle
        handle_x, handle_y = self._get_handle_position()
        handle_color = self.active_handle_color if self._dragging else self.handle_color
        
        pygame.draw.rect(screen, handle_color,
                        (abs_x + handle_x, abs_y + handle_y,
                         self.handle_width, self.handle_height))
        
        # Draw border if set
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(screen, self.border_color,
                           (abs_x, abs_y, self.width, self.height),
                           self.border_width)
