import pygame
from ..component import Component
from ..ui.ui_element import UIElement
from ..ui.panel import Panel
from ..ui.button import Button
from ..ui.label import Label

class UIComponent(Component):
    def __init__(self):
        super().__init__()
        self.root = Panel(0, 0, 800, 600)  # Default to full screen
        self.root.background_color = None  # Transparent by default
        
    def create_panel(self, x: int, y: int, width: int, height: int) -> Panel:
        """Create and add a new panel"""
        panel = Panel(x, y, width, height)
        self.root.add_child(panel)
        return panel
        
    def create_button(self, x: int, y: int, width: int, height: int, text: str) -> Button:
        """Create and add a new button"""
        button = Button(x, y, width, height, text)
        self.root.add_child(button)
        return button
        
    def create_label(self, x: int, y: int, text: str, font_size: int = 24) -> Label:
        """Create and add a new label"""
        label = Label(x, y, text, font_size)
        self.root.add_child(label)
        return label
        
    def add_element(self, element: UIElement):
        """Add an existing UI element"""
        self.root.add_child(element)
        
    def remove_element(self, element: UIElement):
        """Remove a UI element"""
        self.root.remove_child(element)
        
    def set_root_panel(self, panel: Panel):
        """Set a new root panel"""
        self.root = panel
        
    def handle_event(self, event: pygame.event.Event):
        """Handle UI events"""
        if self.enabled:
            # Convert mouse position to UI space if needed
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                # UI always uses screen coordinates, so no conversion needed
                self.root.handle_event(event)
            else:
                self.root.handle_event(event)
            
    def render(self, screen: pygame.Surface, camera_offset=(0, 0)):
        """Render all UI elements - ignore camera offset for UI"""
        if self.enabled:
            # UI is always rendered in screen space, so ignore camera offset
            self.root.render(screen)

    def create_menu(self, x: int, y: int, width: int, height: int,
                   buttons: list[tuple[str, callable]]) -> Panel:
        """
        Create a vertical menu with buttons
        
        Args:
            x: X position of menu
            y: Y position of menu
            width: Width of menu
            height: Height of menu
            buttons: List of (text, callback) tuples for buttons
            
        Returns:
            Panel containing the menu
        """
        menu = self.create_panel(x, y, width, height)
        menu.set_layout(Panel.Layout.VERTICAL, spacing=10)
        
        button_height = 40
        for text, callback in buttons:
            button = Button(0, 0, width - 20, button_height, text)
            button.set_on_click(callback)
            menu.add_child(button)
            
        return menu

    def create_dialog(self, x: int, y: int, width: int, height: int,
                     title: str, content: str) -> Panel:
        """
        Create a dialog box with title and content
        
        Args:
            x: X position of dialog
            y: Y position of dialog
            width: Width of dialog
            height: Height of dialog
            title: Title text
            content: Content text
            
        Returns:
            Panel containing the dialog
        """
        dialog = self.create_panel(x, y, width, height)
        dialog.background_color = (50, 50, 50)
        dialog.border_color = (100, 100, 100)
        dialog.border_width = 2
        
        # Add title
        title_label = Label(10, 10, title, font_size=32)
        dialog.add_child(title_label)
        
        # Add content
        content_label = Label(10, 50, content, font_size=24)
        dialog.add_child(content_label)
        
        return dialog
