import pygame
from typing import Tuple

class Scrollbar:
    def __init__(self, width: int = 10):
        self.width = width
        self.dragging = False
        self.hover = False
        self.scroll_offset = 0
        
        # Colors
        self.background_color = (200, 200, 200)
        self.color = (180, 180, 180)
        self.hover_color = (160, 160, 160)
        self.drag_color = (140, 140, 140)
        
        # Scroll settings
        self.scroll_step = 1  # Lines to scroll per mouse wheel tick
        self.smooth_scroll = True
        
    def handle_mouse_down(self, mouse_pos: Tuple[int, int], component_rect: pygame.Rect) -> bool:
        """Handle mouse down event"""
        scrollbar_rect = pygame.Rect(
            component_rect.right - self.width,
            component_rect.top,
            self.width,
            component_rect.height
        )
        
        if scrollbar_rect.collidepoint(mouse_pos):
            self.dragging = True
            # If clicking on scrollbar track (not handle), jump to that position
            if not self._get_handle_rect(component_rect).collidepoint(mouse_pos):
                self._jump_to_mouse_position(mouse_pos[1], component_rect)
            return True
        return False
        
    def handle_mouse_up(self):
        """Handle mouse up event"""
        self.dragging = False
        
    def handle_mouse_motion(self, mouse_pos: Tuple[int, int], component_rect: pygame.Rect,
                          total_lines: int, visible_lines: int) -> bool:
        """Handle mouse motion event"""
        if self.dragging:
            self._update_scroll_from_mouse(mouse_pos[1], component_rect, total_lines, visible_lines)
            return True
            
        # Update hover state
        scrollbar_rect = pygame.Rect(
            component_rect.right - self.width,
            component_rect.top,
            self.width,
            component_rect.height
        )
        self.hover = scrollbar_rect.collidepoint(mouse_pos)
        return False
        
    def handle_mouse_wheel(self, y: int, total_lines: int, visible_lines: int):
        """Handle mouse wheel event"""
        target_offset = self.scroll_offset - y * self.scroll_step
        self.scroll_offset = max(0, min(target_offset, total_lines - visible_lines))
        
    def ensure_line_visible(self, line: int, total_lines: int, visible_lines: int):
        """Ensure a specific line is visible"""
        # If line is above visible area
        if line < self.scroll_offset:
            self.scroll_offset = line
        # If line is below visible area
        elif line >= self.scroll_offset + visible_lines:
            self.scroll_offset = line - visible_lines + 1
            
        # Clamp scroll offset
        self._clamp_scroll_offset(total_lines, visible_lines)
        
    def _clamp_scroll_offset(self, total_lines: int, visible_lines: int):
        """Clamp scroll offset to valid range"""
        max_scroll = max(0, total_lines - visible_lines)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
        
    def _get_handle_rect(self, component_rect: pygame.Rect) -> pygame.Rect:
        """Get the rectangle for the scrollbar handle"""
        total_height = component_rect.height
        handle_height = max(20, total_height * 0.1)  # Minimum handle size
        handle_y = component_rect.top + (self.scroll_offset / total_height) * (total_height - handle_height)
        
        return pygame.Rect(
            component_rect.right - self.width,
            handle_y,
            self.width,
            handle_height
        )
        
    def _jump_to_mouse_position(self, mouse_y: int, component_rect: pygame.Rect):
        """Jump scroll position to mouse click position"""
        relative_y = (mouse_y - component_rect.top) / component_rect.height
        self.scroll_offset = int(relative_y * component_rect.height)
        
    def _update_scroll_from_mouse(self, mouse_y: int, component_rect: pygame.Rect,
                                total_lines: int, visible_lines: int):
        """Update scroll position from mouse drag"""
        if total_lines <= visible_lines:
            self.scroll_offset = 0
            return
            
        relative_y = mouse_y - component_rect.top
        scroll_ratio = relative_y / component_rect.height
        self.scroll_offset = int(scroll_ratio * (total_lines - visible_lines))
        self._clamp_scroll_offset(total_lines, visible_lines)
        
    def render(self, screen: pygame.Surface, component_rect: pygame.Rect,
              total_lines: int, visible_lines: int):
        """Render scrollbar"""
        if total_lines > visible_lines:
            # Draw scrollbar background
            pygame.draw.rect(screen, self.background_color,
                           (component_rect.right - self.width,
                            component_rect.top,
                            self.width,
                            component_rect.height))
            
            # Calculate scrollbar handle dimensions
            visible_ratio = visible_lines / total_lines
            handle_height = max(20, component_rect.height * visible_ratio)
            handle_y = component_rect.top + (self.scroll_offset / (total_lines - visible_lines)) * (component_rect.height - handle_height)
            
            # Draw scrollbar handle
            color = (self.drag_color if self.dragging else
                    self.hover_color if self.hover else
                    self.color)
            
            pygame.draw.rect(screen, color,
                           (component_rect.right - self.width,
                            handle_y,
                            self.width,
                            handle_height))
