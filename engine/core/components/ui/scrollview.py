import pygame
from typing import Optional, Tuple
from .ui_element import UIElement
from .panel import Panel

class ScrollBar(UIElement):
    def __init__(self, x: int, y: int, width: int, height: int,
                 vertical: bool = True):
        super().__init__(x, y, width, height)
        
        self.vertical = vertical
        self.value = 0.0  # 0.0 to 1.0
        self.handle_size = 0.0  # 0.0 to 1.0
        
        # Style
        self.track_color = (240, 240, 240)
        self.handle_color = (200, 200, 200)
        self.hover_color = (180, 180, 180)
        self.active_color = (160, 160, 160)
        
        # State
        self._dragging = False
        self._drag_start = 0
        self._start_value = 0.0
        self._hovering = False
        
        # Callback
        self.on_value_changed = None
    
    def set_handle_size(self, visible_ratio: float):
        """Set handle size based on visible/total content ratio"""
        self.handle_size = max(0.1, min(1.0, visible_ratio))
    
    def _get_handle_rect(self) -> pygame.Rect:
        """Get handle rectangle in local coordinates"""
        if self.vertical:
            handle_height = int(self.height * self.handle_size)
            handle_pos = int((self.height - handle_height) * self.value)
            return pygame.Rect(0, handle_pos, self.width, handle_height)
        else:
            handle_width = int(self.width * self.handle_size)
            handle_pos = int((self.width - handle_width) * self.value)
            return pygame.Rect(handle_pos, 0, handle_width, self.height)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle scrollbar interaction"""
        if not self.enabled or not self.visible:
            return False
            
        abs_x, abs_y = self.get_absolute_position()
        handle_rect = self._get_handle_rect()
        handle_rect.x += abs_x
        handle_rect.y += abs_y
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if handle_rect.collidepoint(event.pos):
                self._dragging = True
                if self.vertical:
                    self._drag_start = event.pos[1] - handle_rect.y
                else:
                    self._drag_start = event.pos[0] - handle_rect.x
                self._start_value = self.value
                return True
                
            elif self.contains_point(*event.pos):
                # Click on track - jump to position
                if self.vertical:
                    click_pos = (event.pos[1] - abs_y) / self.height
                else:
                    click_pos = (event.pos[0] - abs_x) / self.width
                    
                self.value = max(0.0, min(1.0, click_pos))
                if self.on_value_changed:
                    self.on_value_changed(self.value)
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._dragging = False
            
        elif event.type == pygame.MOUSEMOTION:
            self._hovering = handle_rect.collidepoint(event.pos)
            
            if self._dragging:
                if self.vertical:
                    delta = (event.pos[1] - self._drag_start - abs_y) / (self.height - handle_rect.height)
                else:
                    delta = (event.pos[0] - self._drag_start - abs_x) / (self.width - handle_rect.width)
                    
                self.value = max(0.0, min(1.0, delta))
                if self.on_value_changed:
                    self.on_value_changed(self.value)
                return True
                
        return False
    
    def render(self, screen: pygame.Surface):
        """Render scrollbar"""
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        
        # Draw track
        pygame.draw.rect(screen, self.track_color,
                        (abs_x, abs_y, self.width, self.height))
        
        # Draw handle
        handle_rect = self._get_handle_rect()
        handle_rect.x += abs_x
        handle_rect.y += abs_y
        
        if self._dragging:
            color = self.active_color
        elif self._hovering:
            color = self.hover_color
        else:
            color = self.handle_color
            
        pygame.draw.rect(screen, color, handle_rect)

class ScrollView(Panel):
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)
        
        # Create content panel
        self.content = Panel(0, 0, width, height)
        self.content.clip = False  # Allow content to overflow
        super().add_child(self.content)
        
        # Create scrollbars
        scrollbar_size = 12
        self.vscrollbar = ScrollBar(width - scrollbar_size, 0,
                                  scrollbar_size, height)
        self.vscrollbar.on_value_changed = self._handle_scroll
        super().add_child(self.vscrollbar)
        
        self.hscrollbar = ScrollBar(0, height - scrollbar_size,
                                  width - scrollbar_size, scrollbar_size,
                                  vertical=False)
        self.hscrollbar.on_value_changed = self._handle_scroll
        super().add_child(self.hscrollbar)
        
        # Clip content to view bounds
        self.clip = True
        
        # Track content size
        self._content_width = width
        self._content_height = height
    
    def add_child(self, child: UIElement):
        """Add child to content panel"""
        self.content.add_child(child)
        self._update_content_size()
    
    def remove_child(self, child: UIElement):
        """Remove child from content panel"""
        self.content.remove_child(child)
        self._update_content_size()
    
    def _update_content_size(self):
        """Update content size based on children"""
        self._content_width = max(self.width,
                                max((c.x + c.width for c in self.content.children),
                                    default=self.width))
        self._content_height = max(self.height,
                                 max((c.y + c.height for c in self.content.children),
                                     default=self.height))
        
        # Update scrollbar handle sizes
        self.vscrollbar.set_handle_size(self.height / self._content_height)
        self.hscrollbar.set_handle_size(self.width / self._content_width)
        
        # Show/hide scrollbars based on content size
        self.vscrollbar.visible = self._content_height > self.height
        self.hscrollbar.visible = self._content_width > self.width
        
        # Adjust content position
        self._handle_scroll()
    
    def _handle_scroll(self, value: Optional[float] = None):
        """Update content position based on scroll values"""
        # Vertical scroll
        if self._content_height > self.height:
            max_scroll = self._content_height - self.height
            self.content.y = -int(max_scroll * self.vscrollbar.value)
        else:
            self.content.y = 0
        
        # Horizontal scroll
        if self._content_width > self.width:
            max_scroll = self._content_width - self.width
            self.content.x = -int(max_scroll * self.hscrollbar.value)
        else:
            self.content.x = 0
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle scroll events"""
        if not self.enabled or not self.visible:
            return False
            
        # Handle scrollbar events
        if self.vscrollbar.handle_event(event):
            return True
        if self.hscrollbar.handle_event(event):
            return True
        
        # Handle mouse wheel
        if event.type == pygame.MOUSEWHEEL and self.contains_point(*pygame.mouse.get_pos()):
            if event.y != 0 and self.vscrollbar.visible:
                # Vertical scroll
                scroll_amount = 0.1 * (-event.y)
                self.vscrollbar.value = max(0.0, min(1.0,
                                                   self.vscrollbar.value + scroll_amount))
                self._handle_scroll()
                return True
            elif event.x != 0 and self.hscrollbar.visible:
                # Horizontal scroll
                scroll_amount = 0.1 * (-event.x)
                self.hscrollbar.value = max(0.0, min(1.0,
                                                   self.hscrollbar.value + scroll_amount))
                self._handle_scroll()
                return True
        
        # Handle content events
        return self.content.handle_event(event)
