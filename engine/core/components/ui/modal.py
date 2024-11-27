import pygame
from typing import Tuple, Optional, Callable, List
from .ui_element import UIElement
from .button import Button
from .label import Label
from .panel import Panel

class Modal(UIElement):
    def __init__(self, title: str, content: str, width: int = 400, height: int = 300):
        # Initialize with centered position
        screen_width, screen_height = pygame.display.get_surface().get_size()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        super().__init__(x, y, width, height)
        
        # Style
        self.background_color = (255, 255, 255)  # White
        self.overlay_color = (0, 0, 0, 128)      # Semi-transparent black
        self.title_height = 40
        self.padding = 20
        
        # Create components
        # Title panel
        self.title_panel = Panel(0, 0, width, self.title_height)
        self.title_panel.background_color = (240, 240, 240)  # Light gray
        self.add_child(self.title_panel)
        
        # Title label
        self.title_label = Label(self.padding, 
                               (self.title_height - 24) // 2, 
                               title)
        self.title_label.font = pygame.font.Font(None, 24)
        self.title_panel.add_child(self.title_label)
        
        # Close button
        close_size = 30
        self.close_button = Button(width - close_size - 5, 
                                 (self.title_height - close_size) // 2,
                                 close_size, close_size, "×")
        self.close_button.font = pygame.font.Font(None, 36)
        self.close_button.background_color = None
        self.close_button.hover_color = (220, 220, 220)
        self.close_button.on_click = self.hide
        self.title_panel.add_child(self.close_button)
        
        # Content
        self.content_label = Label(self.padding, 
                                 self.title_height + self.padding,
                                 content)
        self.content_label.font = pygame.font.Font(None, 20)
        self.add_child(self.content_label)
        
        # Buttons panel
        self.buttons_panel = Panel(0, height - 60,
                                 width, 60)
        self.buttons_panel.background_color = (240, 240, 240)
        self.add_child(self.buttons_panel)
        
        # Default buttons
        self.buttons: List[Button] = []
        
        # State
        self._visible = False
        self.result = None
        self.on_close: Optional[Callable[[], None]] = None
    
    def add_button(self, text: str, callback: Optional[Callable[[], None]] = None,
                  primary: bool = False) -> Button:
        """Add a button to the modal"""
        button_width = 100
        button_height = 30
        margin = 10
        
        x = self.width - (len(self.buttons) + 1) * (button_width + margin) - margin
        y = (self.buttons_panel.height - button_height) // 2
        
        button = Button(x, y, button_width, button_height, text)
        if primary:
            button.background_color = (0, 120, 215)  # Blue
            button.text_color = (255, 255, 255)      # White
            button.hover_color = (0, 100, 195)       # Darker blue
        
        if callback:
            button.on_click = callback
        
        self.buttons.append(button)
        self.buttons_panel.add_child(button)
        return button
    
    def show(self):
        """Show the modal"""
        self._visible = True
        self.result = None
    
    def hide(self):
        """Hide the modal"""
        self._visible = False
        if self.on_close:
            self.on_close()
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events"""
        if not self._visible or not self.enabled:
            return False
            
        # Handle children events
        return super().handle_event(event)
    
    def render(self, screen: pygame.Surface):
        """Render modal with overlay"""
        if not self._visible:
            return
            
        # Draw overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill(self.overlay_color)
        screen.blit(overlay, (0, 0))
        
        # Draw modal
        super().render(screen)

class MessageBox(Modal):
    """Convenience class for simple message boxes"""
    def __init__(self, title: str, message: str, 
                 buttons: List[str] = None,
                 on_result: Optional[Callable[[str], None]] = None):
        super().__init__(title, message, width=400, 
                        height=200 if len(message) < 100 else 300)
        
        self.on_result = on_result
        
        # Add default buttons if none provided
        if not buttons:
            buttons = ["OK"]
            
        # Add buttons
        for text in buttons:
            self.add_button(text, lambda t=text: self._handle_result(t),
                          primary=(text == buttons[0]))
    
    def _handle_result(self, result: str):
        """Handle button click"""
        self.result = result
        self.hide()
        if self.on_result:
            self.on_result(result)

class ConfirmDialog(MessageBox):
    """Convenience class for confirmation dialogs"""
    def __init__(self, title: str, message: str,
                 on_confirm: Optional[Callable[[], None]] = None,
                 on_cancel: Optional[Callable[[], None]] = None):
        def handle_result(result: str):
            if result == "Yes" and on_confirm:
                on_confirm()
            elif result == "No" and on_cancel:
                on_cancel()
                
        super().__init__(title, message, ["Yes", "No"], handle_result)
