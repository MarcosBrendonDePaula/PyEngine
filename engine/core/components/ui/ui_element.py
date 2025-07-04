import pygame
from typing import Tuple, Optional

class UIElement:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.enabled = True
        self.parent = None
        self.children = []
        
        # Style properties
        self.background_color = None
        self.border_color = None
        self.border_width = 0
        self.padding = 5
        
        # Entity-like properties for scene compatibility
        self.active = True
        self.scene = None
        self.components = {}
        self.id = id(self)  # Use Python's built-in id() for consistency with Entity
        
    def get_absolute_position(self) -> Tuple[int, int]:
        """Get position considering parent positions"""
        x, y = self.x, self.y
        current = self.parent
        while current:
            x += current.x
            y += current.y
            current = current.parent
        return (x, y)
        
    def add_child(self, child: 'UIElement'):
        """Add a child UI element"""
        if child not in self.children:  # Prevent duplicate children
            if child.parent:
                child.parent.remove_child(child)
            child.parent = self
            self.children.append(child)
        
    def remove_child(self, child: 'UIElement'):
        """Remove a child UI element"""
        if child in self.children:
            child.parent = None
            self.children.remove(child)
            
    def contains_point(self, x: int, y: int) -> bool:
        """Check if point is within element bounds"""
        if not self.visible or not self.enabled:
            return False
            
        abs_x, abs_y = self.get_absolute_position()
        return (abs_x <= x <= abs_x + self.width and 
                abs_y <= y <= abs_y + self.height)
                
    def handle_event(self, event: pygame.event.Event):
        """Handle UI events"""
        if not self.enabled or not self.visible:
            return False
            
        # Handle children events first (in reverse order for proper z-order)
        for child in reversed(self.children):
            if child.handle_event(event):
                return True
                
        return False
        
    def render(self, screen: pygame.Surface):
        """Render the UI element"""
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        
        # Draw background if set
        if self.background_color is not None:  # Allow transparent (None) background
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
            
        # Render children
        for child in self.children:
            child.render(screen)
            
    def set_style(self, 
                  background_color: Optional[Tuple[int, int, int]] = None,
                  border_color: Optional[Tuple[int, int, int]] = None,
                  border_width: int = 0,
                  padding: int = 5):
        """Set style properties"""
        self.background_color = background_color
        self.border_color = border_color
        self.border_width = border_width
        self.padding = padding
        
    def update(self):
        """Update method for scene compatibility"""
        if not self.active:
            return
            
        # Update components if any
        for component in self.components.values():
            if component.enabled:
                component.update()
