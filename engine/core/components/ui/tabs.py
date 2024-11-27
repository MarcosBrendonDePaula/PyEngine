import pygame
from typing import List, Dict, Optional, Callable
from .ui_element import UIElement
from .button import Button
from .panel import Panel

class TabButton(Button):
    """Custom button for tab headers"""
    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        super().__init__(x, y, width, height, text)
        self.active = False
        self.hover_color = (220, 220, 220)
        self.active_color = (255, 255, 255)
        self.inactive_color = (240, 240, 240)
        self.border_color = (200, 200, 200)
        self.border_width = 1
    
    def render(self, screen: pygame.Surface):
        """Render tab button with different styles for active/inactive states"""
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        
        # Background
        if self.active:
            color = self.active_color
        elif self.hovered and self.enabled:
            color = self.hover_color
        else:
            color = self.inactive_color
            
        pygame.draw.rect(screen, color,
                        (abs_x, abs_y, self.width, self.height))
        
        # Border
        if self.border_color and self.border_width > 0:
            if self.active:
                # Draw borders except bottom when active
                pygame.draw.line(screen, self.border_color,
                               (abs_x, abs_y),
                               (abs_x + self.width, abs_y),
                               self.border_width)  # Top
                pygame.draw.line(screen, self.border_color,
                               (abs_x, abs_y),
                               (abs_x, abs_y + self.height),
                               self.border_width)  # Left
                pygame.draw.line(screen, self.border_color,
                               (abs_x + self.width - 1, abs_y),
                               (abs_x + self.width - 1, abs_y + self.height),
                               self.border_width)  # Right
            else:
                pygame.draw.rect(screen, self.border_color,
                               (abs_x, abs_y, self.width, self.height),
                               self.border_width)
        
        # Render label (inherited from Button)
        self.label.render(screen)

class TabPanel(Panel):
    """Panel for tab content"""
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)
        self.background_color = (255, 255, 255)
        self.border_color = (200, 200, 200)
        self.border_width = 1

class Tabs(UIElement):
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)
        
        self.tab_height = 40
        self.tab_padding = 20
        self.min_tab_width = 100
        
        # Initialize font
        self.font = pygame.font.Font(None, 32)
        
        # Create header panel
        self.header = Panel(0, 0, width, self.tab_height)
        self.header.background_color = (240, 240, 240)
        self.header.border_color = (200, 200, 200)
        self.header.border_width = 1
        self.add_child(self.header)
        
        # Create content panel
        self.content = Panel(0, self.tab_height - 1,
                           width, height - self.tab_height + 1)
        self.content.background_color = (255, 255, 255)
        self.content.border_color = (200, 200, 200)
        self.content.border_width = 1
        self.add_child(self.content)
        
        # Tab management
        self.tabs: Dict[str, TabPanel] = {}
        self.buttons: Dict[str, TabButton] = {}
        self.active_tab: Optional[str] = None
        
        # Callback
        self.on_tab_changed: Optional[Callable[[str], None]] = None
    
    def add_tab(self, name: str, title: str) -> TabPanel:
        """Add a new tab"""
        if name in self.tabs:
            raise ValueError(f"Tab '{name}' already exists")
            
        # Create tab panel
        panel = TabPanel(0, 0,
                        self.content.width,
                        self.content.height)
        self.tabs[name] = panel
        
        # Create tab button
        x = sum(btn.width for btn in self.buttons.values())
        width = max(self.min_tab_width,
                   self.font.size(title)[0] + self.tab_padding * 2)
        
        button = TabButton(x, 0, width, self.tab_height, title)
        button.font = self.font  # Use same font as tabs
        button.on_click = lambda: self.set_active_tab(name)
        self.buttons[name] = button
        self.header.add_child(button)
        
        # Set as active if first tab
        if not self.active_tab:
            self.set_active_tab(name)
            
        return panel
    
    def set_active_tab(self, name: str):
        """Switch to specified tab"""
        if name not in self.tabs:
            raise ValueError(f"Tab '{name}' does not exist")
            
        # Update button states
        for tab_name, button in self.buttons.items():
            button.active = (tab_name == name)
            
        # Update content
        self.content.children.clear()
        self.content.add_child(self.tabs[name])
        
        # Store active tab
        old_tab = self.active_tab
        self.active_tab = name
        
        # Trigger callback
        if self.on_tab_changed and old_tab != name:
            self.on_tab_changed(name)
    
    def get_tab(self, name: str) -> Optional[TabPanel]:
        """Get tab panel by name"""
        return self.tabs.get(name)
    
    def remove_tab(self, name: str):
        """Remove a tab"""
        if name not in self.tabs:
            return
            
        # Remove tab and button
        del self.tabs[name]
        self.header.remove_child(self.buttons[name])
        del self.buttons[name]
        
        # Update active tab if needed
        if self.active_tab == name:
            self.active_tab = None
            if self.tabs:
                self.set_active_tab(next(iter(self.tabs)))
                
        # Reposition remaining buttons
        x = 0
        for button in self.buttons.values():
            button.x = x
            x += button.width
