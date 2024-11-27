import pygame
from typing import Tuple, Optional, Callable
from .ui_element import UIElement

class Toggle(UIElement):
    def __init__(self, x: int, y: int, width: int = 60, height: int = 30):
        super().__init__(x, y, width, height)
        
        # State
        self._value = False
        self._animation_progress = 0.0  # 0.0 to 1.0
        self._animating = False
        self._last_update = pygame.time.get_ticks()
        
        # Style
        self.track_color_off = (200, 200, 200)  # Light gray
        self.track_color_on = (0, 150, 136)     # Teal
        self.handle_color = (255, 255, 255)     # White
        self.animation_duration = 200  # ms
        
        # Handle dimensions
        self.handle_padding = 4
        self.handle_radius = (height - 2 * self.handle_padding) // 2
        
        # Callback
        self.on_value_changed: Optional[Callable[[bool], None]] = None
    
    @property
    def value(self) -> bool:
        """Get current state"""
        return self._value
        
    @value.setter
    def value(self, new_value: bool):
        """Set current state and trigger animation"""
        if new_value != self._value:
            self._value = new_value
            self._animating = True
            self._last_update = pygame.time.get_ticks()
            if self.on_value_changed:
                self.on_value_changed(self._value)
    
    def _update_animation(self):
        """Update animation progress"""
        if self._animating:
            current_time = pygame.time.get_ticks()
            dt = current_time - self._last_update
            self._last_update = current_time
            
            target = 1.0 if self._value else 0.0
            speed = 1.0 / self.animation_duration  # progress per ms
            
            if target > self._animation_progress:
                self._animation_progress = min(target, self._animation_progress + speed * dt)
            else:
                self._animation_progress = max(target, self._animation_progress - speed * dt)
                
            if self._animation_progress == target:
                self._animating = False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse click events"""
        if not self.enabled or not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.contains_point(*event.pos):
                self.value = not self._value
                return True
                
        return False
    
    def render(self, screen: pygame.Surface):
        """Render toggle switch with animation"""
        if not self.visible:
            return
            
        self._update_animation()
        
        abs_x, abs_y = self.get_absolute_position()
        
        # Calculate colors based on animation progress
        def lerp_color(color1: Tuple[int, int, int], 
                      color2: Tuple[int, int, int], 
                      t: float) -> Tuple[int, int, int]:
            return tuple(int(a + (b - a) * t) for a, b in zip(color1, color2))
        
        track_color = lerp_color(self.track_color_off, self.track_color_on, 
                               self._animation_progress)
        
        # Draw track (rounded rectangle)
        track_radius = self.height // 2
        track_rect = pygame.Rect(abs_x, abs_y, self.width, self.height)
        
        # Draw track background
        pygame.draw.rect(screen, track_color, track_rect, border_radius=track_radius)
        
        # Calculate handle position
        handle_travel = self.width - 2 * self.handle_padding - 2 * self.handle_radius
        handle_x = abs_x + self.handle_padding + handle_travel * self._animation_progress
        handle_y = abs_y + self.handle_padding
        
        # Draw handle (circle)
        pygame.draw.circle(screen, self.handle_color,
                         (int(handle_x + self.handle_radius), 
                          int(handle_y + self.handle_radius)),
                         self.handle_radius)
        
        # Draw border if set
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(screen, self.border_color, track_rect,
                           self.border_width, border_radius=track_radius)
