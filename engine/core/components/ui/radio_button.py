import pygame
from typing import List, Tuple, Optional, Callable
from .ui_element import UIElement
from .label import Label

class RadioButton(UIElement):
    def __init__(self, x: int, y: int, size: int, text: str):
        super().__init__(x, y, size, size)
        
        self.size = size
        self.checked = False
        self.group = None  # Will be set by RadioGroup
        
        # Colors
        self.outer_color = (100, 100, 100)    # Gray
        self.inner_color = (50, 120, 220)     # Blue
        self.hover_color = (120, 120, 120)    # Light gray
        self.background_color = (255, 255, 255) # White
        
        # Create label
        self.label = Label(size + 10, 0, text)
        self.add_child(self.label)
        self._center_label_vertically()
        
        # State
        self.hovered = False
        
    def _center_label_vertically(self):
        """Center the label vertically relative to the radio button"""
        self.label.y = (self.size - self.label.height) // 2
        
    def set_text(self, text: str):
        """Update radio button text"""
        self.label.set_text(text)
        self._center_label_vertically()
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle radio button events"""
        if not self.enabled or not self.visible:
            return False
            
        # Get mouse position and check hover state
        mouse_pos = pygame.mouse.get_pos()
        abs_x, abs_y = self.get_absolute_position()
        button_rect = pygame.Rect(abs_x, abs_y, self.size, self.size)
        
        was_hovered = self.hovered
        self.hovered = button_rect.collidepoint(mouse_pos)
        
        # Handle click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and not self.checked:
                self.checked = True
                if self.group:
                    self.group._on_button_checked(self)
                return True
                
        return False
        
    def render(self, screen: pygame.Surface):
        """Render the radio button"""
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        center_x = abs_x + self.size // 2
        center_y = abs_y + self.size // 2
        radius = self.size // 2
        inner_radius = radius - 4
        
        # Draw outer circle
        pygame.draw.circle(screen, 
                         self.hover_color if self.hovered else self.outer_color,
                         (center_x, center_y), radius)
        
        # Draw inner circle (background)
        pygame.draw.circle(screen, self.background_color,
                         (center_x, center_y), inner_radius)
        
        # Draw checked indicator
        if self.checked:
            indicator_radius = inner_radius - 4
            pygame.draw.circle(screen, self.inner_color,
                             (center_x, center_y), indicator_radius)
        
        # Render label
        self.label.render(screen)


class RadioGroup(UIElement):
    def __init__(self, x: int, y: int, options: List[str], vertical: bool = True):
        """
        Create a group of radio buttons
        :param vertical: If True, arrange buttons vertically; if False, horizontally
        """
        self.button_size = 20
        self.spacing = 10
        
        # Calculate dimensions based on layout
        if vertical:
            width = 200  # Fixed width for vertical layout
            height = len(options) * (self.button_size + self.spacing) - self.spacing
        else:
            # Calculate width based on text lengths
            font = pygame.font.Font(None, 32)
            max_text_width = max(font.size(text)[0] for text in options)
            width = len(options) * (self.button_size + max_text_width + self.spacing * 2)
            height = self.button_size
            
        super().__init__(x, y, width, height)
        
        self.vertical = vertical
        self.buttons: List[RadioButton] = []
        self.selected_index = -1
        
        # Create radio buttons
        for i, text in enumerate(options):
            if vertical:
                btn_x = 0
                btn_y = i * (self.button_size + self.spacing)
            else:
                btn_x = i * (self.button_size + max_text_width + self.spacing * 2)
                btn_y = 0
                
            button = RadioButton(btn_x, btn_y, self.button_size, text)
            button.group = self
            self.buttons.append(button)
            self.add_child(button)
            
        # Select first button by default if options exist
        if self.buttons:
            self.selected_index = 0
            self.buttons[0].checked = True
            
        # Event handler
        self.on_selection_changed: Optional[Callable[[int, str], None]] = None
        
    def _on_button_checked(self, checked_button: RadioButton):
        """Handle when a button in the group is checked"""
        # Uncheck all other buttons
        for i, button in enumerate(self.buttons):
            if button != checked_button:
                button.checked = False
            elif button.checked:
                self.selected_index = i
                if self.on_selection_changed:
                    self.on_selection_changed(i, button.label.text)
                    
    @property
    def selected_value(self) -> Optional[str]:
        """Get the text of the selected radio button"""
        if 0 <= self.selected_index < len(self.buttons):
            return self.buttons[self.selected_index].label.text
        return None
        
    def set_selected_index(self, index: int):
        """Programmatically select a radio button by index"""
        if 0 <= index < len(self.buttons):
            button = self.buttons[index]
            button.checked = True
            self._on_button_checked(button)
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle radio group events"""
        if not self.enabled or not self.visible:
            return False
            
        # Handle events for all buttons
        for button in self.buttons:
            if button.handle_event(event):
                return True
                
        return False
        
    def render(self, screen: pygame.Surface):
        """Render the radio group"""
        if not self.visible:
            return
            
        # Render all buttons
        for button in self.buttons:
            button.render(screen)
