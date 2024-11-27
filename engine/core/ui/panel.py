import pygame
from typing import List, Tuple, Optional
from .ui_element import UIElement

class Panel(UIElement):
    class Layout:
        VERTICAL = "vertical"
        HORIZONTAL = "horizontal"
        GRID = "grid"

    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)
        self.layout = Panel.Layout.VERTICAL
        self.spacing = 5  # Space between elements
        self.grid_columns = 2  # Default columns for grid layout
        
    def set_layout(self, layout: str, spacing: int = 5):
        """Set the panel's layout style"""
        if layout not in [Panel.Layout.VERTICAL, Panel.Layout.HORIZONTAL, Panel.Layout.GRID]:
            raise ValueError(f"Invalid layout: {layout}")
        self.layout = layout
        self.spacing = spacing
        self._arrange_children()
        
    def set_grid_columns(self, columns: int):
        """Set number of columns for grid layout"""
        self.grid_columns = max(1, columns)
        if self.layout == Panel.Layout.GRID:
            self._arrange_children()
            
    def add_child(self, child: UIElement):
        """Add a child and arrange according to layout"""
        super().add_child(child)
        self._arrange_children()
        
    def remove_child(self, child: UIElement):
        """Remove a child and rearrange remaining children"""
        super().remove_child(child)
        self._arrange_children()
        
    def _arrange_children(self):
        """Arrange children according to current layout"""
        if not self.children:
            return
            
        if self.layout == Panel.Layout.VERTICAL:
            self._arrange_vertical()
        elif self.layout == Panel.Layout.HORIZONTAL:
            self._arrange_horizontal()
        elif self.layout == Panel.Layout.GRID:
            self._arrange_grid()
            
    def _arrange_vertical(self):
        """Arrange children in a vertical layout"""
        current_y = self.padding
        for child in self.children:
            child.x = self.padding
            child.y = current_y
            current_y += child.height + self.spacing
            
    def _arrange_horizontal(self):
        """Arrange children in a horizontal layout"""
        current_x = self.padding
        for child in self.children:
            child.x = current_x
            child.y = self.padding
            current_x += child.width + self.spacing
            
    def _arrange_grid(self):
        """Arrange children in a grid layout"""
        max_width = (self.width - self.padding * 2 - 
                    self.spacing * (self.grid_columns - 1)) // self.grid_columns
                    
        current_x = self.padding
        current_y = self.padding
        col = 0
        
        for child in self.children:
            child.x = current_x
            child.y = current_y
            
            col += 1
            if col >= self.grid_columns:
                col = 0
                current_x = self.padding
                current_y += max(
                    [c.height for c in self.children[max(0, len(self.children)-self.grid_columns):]]
                ) + self.spacing
            else:
                current_x += max_width + self.spacing
                
    def set_size(self, width: int, height: int):
        """Update panel size and rearrange children"""
        self.width = width
        self.height = height
        self._arrange_children()

    def render(self, screen: pygame.Surface):
        """Render the panel and its children"""
        if not self.visible:
            return
            
        # Get absolute position for rendering
        abs_x, abs_y = self.get_absolute_position()
        
        # Draw panel background if set
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
        
        # Render children
        for child in self.children:
            child.render(screen)
