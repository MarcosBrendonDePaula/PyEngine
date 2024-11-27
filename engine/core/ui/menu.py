import pygame
from typing import List, Dict, Optional, Callable, Union
from .ui_element import UIElement
from .button import Button
from .panel import Panel

class MenuItem:
    def __init__(self, text: str, 
                 callback: Optional[Callable[[], None]] = None,
                 submenu: Optional[List['MenuItem']] = None):
        self.text = text
        self.callback = callback
        self.submenu = submenu or []
        self.parent: Optional['MenuItem'] = None
        
        # Set parent reference for submenu items
        for item in self.submenu:
            item.parent = self

class MenuButton(Button):
    """Button for menu items"""
    def __init__(self, x: int, y: int, width: int, height: int, 
                 text: str, has_submenu: bool = False):
        super().__init__(x, y, width, height, text)
        self.has_submenu = has_submenu
        self.hover_color = (220, 220, 220)
        self.text_color = (0, 0, 0)
        self.arrow_color = (100, 100, 100)
        self.padding = 10
    
    def render(self, screen: pygame.Surface):
        """Render menu button with submenu arrow if needed"""
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        
        # Background
        if self._hovering and self.enabled:
            color = self.hover_color
        else:
            color = self.background_color or (255, 255, 255)
            
        pygame.draw.rect(screen, color,
                        (abs_x, abs_y, self.width, self.height))
        
        # Text
        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_x = abs_x + self.padding
            text_y = abs_y + (self.height - text_surface.get_height()) // 2
            screen.blit(text_surface, (text_x, text_y))
        
        # Submenu arrow
        if self.has_submenu:
            arrow_size = 8
            arrow_x = abs_x + self.width - arrow_size - self.padding
            arrow_y = abs_y + (self.height - arrow_size) // 2
            
            points = [
                (arrow_x, arrow_y),
                (arrow_x, arrow_y + arrow_size),
                (arrow_x + arrow_size, arrow_y + arrow_size // 2)
            ]
            pygame.draw.polygon(screen, self.arrow_color, points)

class MenuPanel(Panel):
    """Panel for menu items"""
    def __init__(self, x: int, y: int, width: int):
        super().__init__(x, y, width, 0)  # Height will be set based on items
        self.background_color = (255, 255, 255)
        self.border_color = (200, 200, 200)
        self.border_width = 1
        self.item_height = 30
        self.min_width = 150
        
        # Shadow effect
        self.shadow_color = (0, 0, 0, 30)
        self.shadow_offset = 4
    
    def render(self, screen: pygame.Surface):
        """Render menu panel with shadow effect"""
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        
        # Draw shadow
        shadow_surface = pygame.Surface((self.width + self.shadow_offset,
                                       self.height + self.shadow_offset),
                                      pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, self.shadow_color,
                        (self.shadow_offset, self.shadow_offset,
                         self.width, self.height))
        screen.blit(shadow_surface, (abs_x, abs_y))
        
        # Draw panel
        super().render(screen)

class Menu(UIElement):
    def __init__(self, x: int, y: int, items: List[MenuItem]):
        super().__init__(x, y, 0, 0)  # Size will be calculated
        
        self.items = items
        self.item_height = 30
        self.padding = 10
        self.min_width = 150
        
        # Initialize font
        self.font = pygame.font.Font(None, 32)
        
        # Active submenus
        self.active_panels: List[MenuPanel] = []
        
        # Create root panel
        self._create_panel(items, x, y)
    
    def _create_panel(self, items: List[MenuItem], x: int, y: int) -> MenuPanel:
        """Create a menu panel with given items"""
        # Calculate panel size
        width = self.min_width
        for item in items:
            text_width = self.font.size(item.text)[0] + self.padding * 3
            width = max(width, text_width)
        
        height = len(items) * self.item_height
        
        # Create panel
        panel = MenuPanel(x, y, width)
        panel.height = height
        
        # Create buttons for items
        for i, item in enumerate(items):
            button = MenuButton(0, i * self.item_height,
                              width, self.item_height,
                              item.text,
                              bool(item.submenu))
            button.font = self.font  # Use same font as menu
            
            if item.callback:
                button.on_click = lambda i=item: self._handle_click(i)
            
            if item.submenu:
                button.on_hover = lambda i=item, b=button: self._show_submenu(i, b)
                
            panel.add_child(button)
        
        return panel
    
    def _handle_click(self, item: MenuItem):
        """Handle menu item click"""
        if item.callback:
            item.callback()
        self.hide()
    
    def _show_submenu(self, item: MenuItem, button: MenuButton):
        """Show submenu for item"""
        if not item.submenu:
            return
            
        # Remove any existing submenus at this level and deeper
        while self.active_panels and self.active_panels[-1] != button.parent:
            panel = self.active_panels.pop()
            panel.visible = False
        
        # Create new submenu panel
        abs_x, abs_y = button.get_absolute_position()
        panel = self._create_panel(item.submenu,
                                 abs_x + button.width,
                                 abs_y)
        
        # Add to active panels
        self.active_panels.append(panel)
        self.add_child(panel)
    
    def show(self):
        """Show menu"""
        self.visible = True
    
    def hide(self):
        """Hide menu and all submenus"""
        self.visible = False
        for panel in self.active_panels:
            panel.visible = False
        self.active_panels.clear()
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events"""
        if not self.visible or not self.enabled:
            return False
            
        # Handle mouse events
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Hide menu if clicked outside
            if not any(panel.contains_point(*event.pos) 
                      for panel in [self] + self.active_panels):
                self.hide()
                return True
        
        return super().handle_event(event)
