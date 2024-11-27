import pygame
from typing import Tuple, Optional
from .ui_element import UIElement
from .label import Label

class Tooltip(UIElement):
    def __init__(self, text: str, padding: int = 8):
        # Initialize with zero size - will be calculated based on text
        super().__init__(0, 0, 0, 0)
        
        self.padding = padding
        self.show_delay = 500  # ms before showing tooltip
        self.fade_duration = 200  # ms for fade animation
        
        # Style
        self.background_color = (50, 50, 50, 230)  # Dark gray with alpha
        self.text_color = (255, 255, 255)  # White
        self.font_size = 16
        
        # Create label for text
        self.label = Label(padding, padding, text)
        self.label.font = pygame.font.Font(None, self.font_size)
        self.label.text_color = self.text_color
        self.add_child(self.label)
        
        # Calculate size based on text
        text_width, text_height = self.label.font.size(text)
        self.width = text_width + 2 * padding
        self.height = text_height + 2 * padding
        
        # State
        self.hover_start = 0
        self.fade_start = 0
        self.alpha = 0  # Current opacity
        self._visible = False
        self._fading_out = False
    
    def show(self, pos: Tuple[int, int]):
        """Show tooltip at specified position"""
        x, y = pos
        
        # Position tooltip above mouse cursor
        self.x = x
        self.y = y - self.height - 10  # 10px gap from cursor
        
        # Keep tooltip within screen bounds
        screen_width, screen_height = pygame.display.get_surface().get_size()
        
        # Adjust horizontal position
        if self.x + self.width > screen_width:
            self.x = screen_width - self.width
        if self.x < 0:
            self.x = 0
            
        # Adjust vertical position
        if self.y < 0:
            # Show below cursor if not enough space above
            self.y = y + 20
            
        # Start showing
        if not self._visible and not self._fading_out:
            self.hover_start = pygame.time.get_ticks()
            self._visible = True
    
    def hide(self):
        """Start hiding tooltip with fade animation"""
        if self._visible and not self._fading_out:
            self._fading_out = True
            self.fade_start = pygame.time.get_ticks()
    
    def update(self):
        """Update tooltip animation"""
        current_time = pygame.time.get_ticks()
        
        if self._visible and not self._fading_out:
            # Fade in
            if current_time - self.hover_start >= self.show_delay:
                progress = min(1.0, (current_time - (self.hover_start + self.show_delay)) 
                             / self.fade_duration)
                self.alpha = int(255 * progress)
        
        elif self._fading_out:
            # Fade out
            progress = (current_time - self.fade_start) / self.fade_duration
            if progress >= 1.0:
                self._visible = False
                self._fading_out = False
                self.alpha = 0
            else:
                self.alpha = int(255 * (1.0 - progress))
    
    def render(self, screen: pygame.Surface):
        """Render tooltip with fade effect"""
        if not self._visible:
            return
            
        self.update()
        
        if self.alpha > 0:
            abs_x, abs_y = self.get_absolute_position()
            
            # Create surface with alpha channel
            surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Draw background with current alpha
            background_color = (*self.background_color[:3], 
                              int(self.background_color[3] * self.alpha / 255))
            pygame.draw.rect(surface, background_color,
                           (0, 0, self.width, self.height),
                           border_radius=4)
            
            # Update label alpha
            self.label.text_color = (*self.text_color, self.alpha)
            
            # Render label to surface
            self.label.render(surface)
            
            # Blit surface to screen
            screen.blit(surface, (abs_x, abs_y))

class TooltipMixin:
    """Mixin class to add tooltip functionality to UI elements"""
    def __init__(self, tooltip_text: Optional[str] = None):
        self.tooltip_text = tooltip_text
        self.tooltip: Optional[Tooltip] = None
        self._is_hovering = False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for tooltip"""
        if not hasattr(super(), 'handle_event'):
            return False
            
        if not self.enabled or not self.visible or not self.tooltip_text:
            return super().handle_event(event)
            
        result = super().handle_event(event)
        
        if event.type == pygame.MOUSEMOTION:
            if self.contains_point(*event.pos):
                if not self._is_hovering:
                    self._is_hovering = True
                    if not self.tooltip:
                        self.tooltip = Tooltip(self.tooltip_text)
                    self.tooltip.show(event.pos)
            elif self._is_hovering:
                self._is_hovering = False
                if self.tooltip:
                    self.tooltip.hide()
                    
        return result
    
    def render(self, screen: pygame.Surface):
        """Render element and tooltip"""
        if not hasattr(super(), 'render'):
            return
            
        super().render(screen)
        
        if self.tooltip and self._is_hovering:
            self.tooltip.render(screen)
