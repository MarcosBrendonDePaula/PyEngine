import pygame
from typing import Callable, Optional
from .ui_element import UIElement
from .label import Label

class Checkbox(UIElement):
    """Simple checkbox component with optional text label."""

    def __init__(self, x: int, y: int, size: int = 20, text: str = ""):
        super().__init__(x, y, size, size)
        self.size = size
        self.checked = False
        self.hovered = False

        # Colors
        self.box_color = (100, 100, 100)       # Gray
        self.check_color = (50, 120, 220)      # Blue
        self.hover_color = (120, 120, 120)     # Light gray
        self.background_color = (255, 255, 255)  # White

        # Optional label
        self.label = Label(size + 10, 0, text) if text else None
        if self.label:
            self.add_child(self.label)
            self._center_label_vertically()

        # Callback when value changes
        self.on_value_changed: Optional[Callable[[bool], None]] = None

    def _center_label_vertically(self):
        if self.label:
            self.label.y = (self.size - self.label.height) // 2

    def set_text(self, text: str):
        if self.label:
            self.label.set_text(text)
        else:
            self.label = Label(self.size + 10, 0, text)
            self.add_child(self.label)
        self._center_label_vertically()

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.enabled or not self.visible:
            return False

        mouse_pos = pygame.mouse.get_pos()
        abs_x, abs_y = self.get_absolute_position()
        rect = pygame.Rect(abs_x, abs_y, self.size, self.size)
        self.hovered = rect.collidepoint(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.checked = not self.checked
                if self.on_value_changed:
                    self.on_value_changed(self.checked)
                return True
        return False

    def render(self, screen: pygame.Surface):
        if not self.visible:
            return

        abs_x, abs_y = self.get_absolute_position()
        color = self.hover_color if self.hovered else self.box_color

        # Outer box
        pygame.draw.rect(screen, color, (abs_x, abs_y, self.size, self.size))
        # Inner background
        pygame.draw.rect(screen, self.background_color,
                         (abs_x + 2, abs_y + 2, self.size - 4, self.size - 4))

        # Check mark
        if self.checked:
            pygame.draw.line(screen, self.check_color,
                             (abs_x + 4, abs_y + self.size // 2),
                             (abs_x + self.size // 3, abs_y + self.size - 4), 3)
            pygame.draw.line(screen, self.check_color,
                             (abs_x + self.size // 3, abs_y + self.size - 4),
                             (abs_x + self.size - 4, abs_y + 4), 3)

        if self.label:
            self.label.render(screen)
