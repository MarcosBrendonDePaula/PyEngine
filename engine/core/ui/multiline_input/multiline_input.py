import pygame
from typing import Optional
from ..input import Input
from .cursor import Cursor
from .scrollbar import Scrollbar
from .key_handler import KeyHandler
from .text_manager import TextManager

class MultilineInput(Input):
    def __init__(self, x: int, y: int, width: int, height: int, placeholder: str = ""):
        super().__init__(x, y, width, height, placeholder)
        
        # Components
        self.cursor = Cursor()
        self.scrollbar = Scrollbar()
        self.key_handler = KeyHandler()
        self.text_manager = TextManager()
        
        # Line metrics
        self.line_height = self.font.get_linesize()
        self.visible_lines = height // self.line_height
        
        # Connect text manager events
        self.text_manager.on_text_changed = self._on_text_changed
        
    def set_text(self, text: str):
        """Set the input text"""
        self.text_manager.set_text(text)
        self.cursor.set_position(len(text), len(text))
        self._ensure_cursor_visible()
        
    def _on_text_changed(self, text: str):
        """Handle text changes"""
        self.text = text
        if self.on_text_changed:
            self.on_text_changed(text)
            
    def _ensure_cursor_visible(self):
        """Ensure cursor is visible"""
        line, _ = self.cursor.get_position_in_lines(self.text_manager.lines)
        self.scrollbar.ensure_line_visible(line, len(self.text_manager.lines), self.visible_lines)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events"""
        if not self.enabled or not self.visible:
            return False
            
        current_time = pygame.time.get_ticks()
            
        # Handle scrollbar events
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.scrollbar.handle_mouse_down(event.pos, self.get_absolute_rect()):
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.scrollbar.handle_mouse_up()
            
        elif event.type == pygame.MOUSEMOTION:
            if self.scrollbar.handle_mouse_motion(event.pos, self.get_absolute_rect(),
                                                len(self.text_manager.lines), self.visible_lines):
                return True
                
        # Handle mouse wheel scrolling
        elif event.type == pygame.MOUSEWHEEL and self.contains_point(*pygame.mouse.get_pos()):
            self.scrollbar.handle_mouse_wheel(event.y, len(self.text_manager.lines), self.visible_lines)
            return True
            
        # Handle text input when focused
        if self.focused:
            if event.type == pygame.TEXTINPUT:
                # Check if text would exceed width
                line, column = self.cursor.get_position_in_lines(self.text_manager.lines)
                current_line = self.text_manager.lines[line]
                test_line = current_line[:column] + event.text + current_line[column:]
                if self.font.size(test_line)[0] <= self.width - self.scrollbar.width - self.padding * 2:
                    self.text_manager.insert_text(self.cursor.position, event.text)
                    self.cursor.move_right(len(self.text))
                    self._ensure_cursor_visible()
                return True
                
            elif event.type == pygame.KEYDOWN:
                # Handle key repeat
                is_new_key = self.key_handler.handle_key_down(event, current_time)
                
                if event.key == pygame.K_RETURN:
                    self.text_manager.insert_newline(self.cursor.position)
                    self.cursor.move_right(len(self.text))
                    self._ensure_cursor_visible()
                    return True
                    
                elif event.key == pygame.K_BACKSPACE:
                    if self.cursor.position > 0:
                        self.text_manager.delete_text(self.cursor.position - 1, self.cursor.position)
                        self.cursor.move_left(len(self.text))
                        self._ensure_cursor_visible()
                    return True
                    
                elif event.key == pygame.K_DELETE:
                    if self.cursor.position < len(self.text):
                        self.text_manager.delete_text(self.cursor.position, self.cursor.position + 1)
                        self._ensure_cursor_visible()
                    return True
                    
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                    if event.key == pygame.K_LEFT:
                        self.cursor.move_left(len(self.text))
                    elif event.key == pygame.K_RIGHT:
                        self.cursor.move_right(len(self.text))
                    elif event.key == pygame.K_UP:
                        self.cursor.move_up(self.text_manager.lines)
                    elif event.key == pygame.K_DOWN:
                        self.cursor.move_down(self.text_manager.lines)
                    self._ensure_cursor_visible()
                    return True
                    
            # Handle key repeat
            keys = pygame.key.get_pressed()
            if self.key_handler.handle_key_repeat(current_time, keys):
                if self.key_handler.is_repeating(pygame.K_BACKSPACE):
                    if self.cursor.position > 0:
                        self.text_manager.delete_text(self.cursor.position - 1, self.cursor.position)
                        self.cursor.move_left(len(self.text))
                        self._ensure_cursor_visible()
                elif self.key_handler.is_repeating(pygame.K_DELETE):
                    if self.cursor.position < len(self.text):
                        self.text_manager.delete_text(self.cursor.position, self.cursor.position + 1)
                        self._ensure_cursor_visible()
                elif self.key_handler.is_repeating(pygame.K_LEFT):
                    self.cursor.move_left(len(self.text))
                    self._ensure_cursor_visible()
                elif self.key_handler.is_repeating(pygame.K_RIGHT):
                    self.cursor.move_right(len(self.text))
                    self._ensure_cursor_visible()
                elif self.key_handler.is_repeating(pygame.K_UP):
                    self.cursor.move_up(self.text_manager.lines)
                    self._ensure_cursor_visible()
                elif self.key_handler.is_repeating(pygame.K_DOWN):
                    self.cursor.move_down(self.text_manager.lines)
                    self._ensure_cursor_visible()
                    
        # Handle focus
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            was_focused = self.focused
            self.focused = self.contains_point(*event.pos)
            if self.focused and not was_focused:
                pygame.key.start_text_input()
            elif not self.focused and was_focused:
                pygame.key.stop_text_input()
                self.key_handler.reset()
            return self.focused
            
        return False
        
    def get_absolute_rect(self) -> pygame.Rect:
        """Get absolute rectangle for component"""
        abs_x, abs_y = self.get_absolute_position()
        return pygame.Rect(abs_x, abs_y, self.width, self.height)
        
    def render(self, screen: pygame.Surface):
        """Render the multiline input field"""
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        
        # Create clip rect for text area
        text_rect = pygame.Rect(
            abs_x + self.padding,
            abs_y,
            self.width - self.scrollbar.width - self.padding * 2,
            self.height
        )
        
        # Draw background
        pygame.draw.rect(screen, self.background_color,
                        (abs_x, abs_y, self.width, self.height))
        
        # Set clip area to prevent text from rendering outside bounds
        old_clip = screen.get_clip()
        screen.set_clip(text_rect)
        
        # Draw visible lines
        y = abs_y
        visible_range = range(self.scrollbar.scroll_offset,
                            min(len(self.text_manager.lines),
                                self.scrollbar.scroll_offset + self.visible_lines))
        
        for i in visible_range:
            line = self.text_manager.lines[i]
            if line:
                line_surface = self.font.render(line, True, self.text_color)
                screen.blit(line_surface, (abs_x + self.padding, y))
            y += self.line_height
            
        # Draw cursor if focused
        if self.focused and pygame.time.get_ticks() % 1000 < 500:
            line, column = self.cursor.get_position_in_lines(self.text_manager.lines)
            if self.scrollbar.scroll_offset <= line < self.scrollbar.scroll_offset + self.visible_lines:
                cursor_x = abs_x + self.padding + self.font.size(self.text_manager.lines[line][:column])[0]
                cursor_y = abs_y + (line - self.scrollbar.scroll_offset) * self.line_height
                pygame.draw.line(screen, self.text_color,
                               (cursor_x, cursor_y),
                               (cursor_x, cursor_y + self.line_height))
        
        # Restore clip area
        screen.set_clip(old_clip)
        
        # Draw scrollbar
        self.scrollbar.render(screen, self.get_absolute_rect(),
                            len(self.text_manager.lines), self.visible_lines)
        
        # Draw border
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(screen, self.border_color,
                           (abs_x, abs_y, self.width, self.height),
                           self.border_width)
