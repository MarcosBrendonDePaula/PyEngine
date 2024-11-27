import pygame
from typing import Optional, Tuple
from .ui_element import UIElement
from .panel import Panel
from .label import Label

class TitledPanel(Panel):
    def __init__(self, x: int, y: int, width: int, height: int, title: str):
        super().__init__(x, y, width, height)
        
        self.title_height = 30
        self.padding = 10
        
        # Style
        self.background_color = (255, 255, 255)
        self.border_color = (200, 200, 200)
        self.border_width = 1
        self.title_background_color = (240, 240, 240)
        self.title_text_color = (0, 0, 0)
        
        # Create title panel
        self.title_panel = Panel(0, 0, width, self.title_height)
        self.title_panel.background_color = self.title_background_color
        self.title_panel.border_color = self.border_color
        self.title_panel.border_width = self.border_width
        super().add_child(self.title_panel)
        
        # Create title label
        self.title_label = Label(self.padding, 0, title)
        self.title_label.height = self.title_height
        self.title_label.text_color = self.title_text_color
        self.title_panel.add_child(self.title_label)
        
        # Create content panel
        self.content = Panel(0, self.title_height,
                           width, height - self.title_height)
        self.content.background_color = self.background_color
        self.content.border_color = self.border_color
        self.content.border_width = self.border_width
        super().add_child(self.content)
    
    def add_child(self, child: UIElement):
        """Add child to content panel"""
        self.content.add_child(child)
    
    def remove_child(self, child: UIElement):
        """Remove child from content panel"""
        self.content.remove_child(child)
    
    @property
    def title(self) -> str:
        """Get panel title"""
        return self.title_label.text
    
    @title.setter
    def title(self, value: str):
        """Set panel title"""
        self.title_label.text = value
    
    def set_style(self, background_color: Optional[Tuple[int, int, int]] = None,
                 border_color: Optional[Tuple[int, int, int]] = None,
                 title_background_color: Optional[Tuple[int, int, int]] = None,
                 title_text_color: Optional[Tuple[int, int, int]] = None):
        """Set panel style colors"""
        if background_color is not None:
            self.background_color = background_color
            self.content.background_color = background_color
            
        if border_color is not None:
            self.border_color = border_color
            self.content.border_color = border_color
            self.title_panel.border_color = border_color
            
        if title_background_color is not None:
            self.title_background_color = title_background_color
            self.title_panel.background_color = title_background_color
            
        if title_text_color is not None:
            self.title_text_color = title_text_color
            self.title_label.text_color = title_text_color
