import pygame
from typing import Optional, Tuple, Union
from .ui_element import UIElement

class Image(UIElement):
    def __init__(self, x: int, y: int, width: int, height: int,
                 image: Optional[Union[str, pygame.Surface]] = None):
        super().__init__(x, y, width, height)
        
        self._surface: Optional[pygame.Surface] = None
        self._original_surface: Optional[pygame.Surface] = None
        self.tint_color: Optional[Tuple[int, int, int]] = None
        self.alpha = 255
        self.scale_mode = 'fit'  # 'fit', 'fill', 'stretch'
        
        if image:
            self.set_image(image)
    
    def set_image(self, image: Union[str, pygame.Surface]):
        """Set image from file path or surface"""
        if isinstance(image, str):
            self._original_surface = pygame.image.load(image).convert_alpha()
        else:
            self._original_surface = image.convert_alpha()
            
        self._update_surface()
    
    def _update_surface(self):
        """Update displayed surface based on current properties"""
        if not self._original_surface:
            return
            
        # Calculate new size based on scale mode
        orig_width = self._original_surface.get_width()
        orig_height = self._original_surface.get_height()
        
        if self.scale_mode == 'stretch':
            new_width = self.width
            new_height = self.height
        else:
            # Calculate scaling factors
            scale_x = self.width / orig_width
            scale_y = self.height / orig_height
            
            if self.scale_mode == 'fit':
                scale = min(scale_x, scale_y)
            else:  # 'fill'
                scale = max(scale_x, scale_y)
                
            new_width = int(orig_width * scale)
            new_height = int(orig_height * scale)
        
        # Scale image
        scaled = pygame.transform.smoothscale(self._original_surface,
                                           (new_width, new_height))
        
        # Apply tint if set
        if self.tint_color:
            tint_surface = pygame.Surface((new_width, new_height),
                                        pygame.SRCALPHA)
            tint_surface.fill((*self.tint_color, self.alpha))
            scaled.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Set alpha
        if self.alpha != 255:
            scaled.set_alpha(self.alpha)
        
        self._surface = scaled
    
    def set_tint(self, color: Optional[Tuple[int, int, int]]):
        """Set tint color"""
        if self.tint_color != color:
            self.tint_color = color
            self._update_surface()
    
    def set_alpha(self, alpha: int):
        """Set transparency (0-255)"""
        alpha = max(0, min(255, alpha))
        if self.alpha != alpha:
            self.alpha = alpha
            self._update_surface()
    
    def set_scale_mode(self, mode: str):
        """Set scale mode ('fit', 'fill', or 'stretch')"""
        if mode in ('fit', 'fill', 'stretch') and self.scale_mode != mode:
            self.scale_mode = mode
            self._update_surface()
    
    def render(self, screen: pygame.Surface):
        """Render image"""
        if not self.visible or not self._surface:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        
        # Center image in available space
        x_offset = (self.width - self._surface.get_width()) // 2
        y_offset = (self.height - self._surface.get_height()) // 2
        
        screen.blit(self._surface, (abs_x + x_offset, abs_y + y_offset))
        
        # Draw border if set
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(screen, self.border_color,
                           (abs_x, abs_y, self.width, self.height),
                           self.border_width)

class Icon(Image):
    """Convenience class for small icons"""
    def __init__(self, x: int, y: int, size: int,
                 image: Optional[Union[str, pygame.Surface]] = None):
        super().__init__(x, y, size, size, image)
        self.scale_mode = 'stretch'  # Icons typically stretch to fill their space
