import pygame
from typing import Tuple, Optional, Callable
from .ui_element import UIElement

class Input(UIElement):
    def __init__(self, x: int, y: int, width: int, height: int, placeholder: str = ""):
        super().__init__(x, y, width, height)
        
        # Text properties
        self.text = ""
        self.placeholder = placeholder
        self.cursor_pos = 0
        self.selection_start = None
        self.font = pygame.font.Font(None, 32)  # Default font
        
        # Colors
        self.text_color = (0, 0, 0)           # Black
        self.background_color = (255, 255, 255) # White
        self.placeholder_color = (128, 128, 128) # Gray
        self.selection_color = (0, 120, 215, 128) # Semi-transparent blue
        self.border_color = (100, 100, 100)    # Gray
        self.border_width = 1
        
        # State
        self.focused = False
        self.cursor_visible = True
        self.cursor_blink_time = 0
        
        # Event handler
        self.on_text_changed: Optional[Callable[[str], None]] = None
        
    def set_text(self, text: str):
        """Set the input text"""
        self.text = text
        self.cursor_pos = len(text)
        if self.on_text_changed:
            self.on_text_changed(self.text)
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events"""
        if not self.enabled or not self.visible:
            return False
            
        # Handle focus
        if event.type == pygame.MOUSEBUTTONDOWN:
            was_focused = self.focused
            self.focused = self.contains_point(*event.pos)
            if self.focused and not was_focused:
                # Start text input
                pygame.key.start_text_input()
            elif not self.focused and was_focused:
                # Stop text input
                pygame.key.stop_text_input()
            return self.focused
            
        if not self.focused:
            return False
            
        # Handle text input
        if event.type == pygame.TEXTINPUT:
            if self.selection_start is not None:
                # Replace selected text
                start = min(self.selection_start, self.cursor_pos)
                end = max(self.selection_start, self.cursor_pos)
                self.text = self.text[:start] + event.text + self.text[end:]
                self.cursor_pos = start + len(event.text)
                self.selection_start = None
            else:
                # Insert text at cursor
                self.text = self.text[:self.cursor_pos] + event.text + self.text[self.cursor_pos:]
                self.cursor_pos += len(event.text)
            if self.on_text_changed:
                self.on_text_changed(self.text)
            return True
            
        # Handle special keys
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if self.selection_start is not None:
                    # Delete selected text
                    start = min(self.selection_start, self.cursor_pos)
                    end = max(self.selection_start, self.cursor_pos)
                    self.text = self.text[:start] + self.text[end:]
                    self.cursor_pos = start
                    self.selection_start = None
                elif self.cursor_pos > 0:
                    # Delete character before cursor
                    self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
                if self.on_text_changed:
                    self.on_text_changed(self.text)
                return True
                
            elif event.key == pygame.K_DELETE:
                if self.selection_start is not None:
                    # Delete selected text
                    start = min(self.selection_start, self.cursor_pos)
                    end = max(self.selection_start, self.cursor_pos)
                    self.text = self.text[:start] + self.text[end:]
                    self.cursor_pos = start
                    self.selection_start = None
                elif self.cursor_pos < len(self.text):
                    # Delete character after cursor
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
                if self.on_text_changed:
                    self.on_text_changed(self.text)
                return True
                
            elif event.key == pygame.K_LEFT:
                if event.mod & pygame.KMOD_SHIFT:
                    # Start or extend selection
                    if self.selection_start is None:
                        self.selection_start = self.cursor_pos
                else:
                    # Clear selection
                    self.selection_start = None
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
                return True
                
            elif event.key == pygame.K_RIGHT:
                if event.mod & pygame.KMOD_SHIFT:
                    # Start or extend selection
                    if self.selection_start is None:
                        self.selection_start = self.cursor_pos
                else:
                    # Clear selection
                    self.selection_start = None
                if self.cursor_pos < len(self.text):
                    self.cursor_pos += 1
                return True
                
        return False
        
    def render(self, screen: pygame.Surface):
        """Render the input field"""
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        
        # Draw background
        pygame.draw.rect(screen, self.background_color,
                        (abs_x, abs_y, self.width, self.height))
        
        # Draw text or placeholder
        text_surface = None
        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
        elif self.placeholder:
            text_surface = self.font.render(self.placeholder, True, self.placeholder_color)
            
        if text_surface:
            # Center text vertically
            text_y = abs_y + (self.height - text_surface.get_height()) // 2
            screen.blit(text_surface, (abs_x + self.padding, text_y))
            
        # Draw selection if any
        if self.focused and self.selection_start is not None:
            start_pos = min(self.selection_start, self.cursor_pos)
            end_pos = max(self.selection_start, self.cursor_pos)
            if start_pos != end_pos:
                start_text = self.text[:start_pos]
                selected_text = self.text[start_pos:end_pos]
                start_width = self.font.size(start_text)[0]
                selection_width = self.font.size(selected_text)[0]
                selection_surface = pygame.Surface((selection_width, self.height), pygame.SRCALPHA)
                selection_surface.fill(self.selection_color)
                screen.blit(selection_surface, (abs_x + self.padding + start_width, abs_y))
        
        # Draw cursor if focused
        if self.focused and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = abs_x + self.padding
            if self.text:
                cursor_x += self.font.size(self.text[:self.cursor_pos])[0]
            pygame.draw.line(screen, self.text_color,
                           (cursor_x, abs_y + 5),
                           (cursor_x, abs_y + self.height - 5))
        
        # Draw border
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(screen, self.border_color,
                           (abs_x, abs_y, self.width, self.height),
                           self.border_width)
