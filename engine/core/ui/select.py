import pygame
from typing import List, Tuple, Optional, Callable
from .ui_element import UIElement

class Select(UIElement):
    def __init__(self, x: int, y: int, width: int, height: int, options: List[str] = None):
        super().__init__(x, y, width, height)
        
        # Options
        self.options = options or []
        self.selected_index = -1
        self.dropdown_open = False
        self.hover_index = -1
        
        # Appearance
        self.font = pygame.font.Font(None, 32)
        self.item_height = 30
        self.max_visible_items = 5
        
        # Colors
        self.text_color = (0, 0, 0)           # Black
        self.background_color = (255, 255, 255) # White
        self.hover_color = (230, 230, 230)     # Light gray
        self.selected_color = (200, 200, 255)  # Light blue
        self.border_color = (100, 100, 100)    # Gray
        self.border_width = 1
        
        # Arrow indicator
        self.arrow_color = (100, 100, 100)
        self.arrow_size = 10
        
        # Event handler
        self.on_selection_changed: Optional[Callable[[int, str], None]] = None
        
    def set_options(self, options: List[str]):
        """Set the list of options"""
        self.options = options
        self.selected_index = -1 if not options else 0
        self.dropdown_open = False
        
    @property
    def selected_value(self) -> Optional[str]:
        """Get the currently selected value"""
        if 0 <= self.selected_index < len(self.options):
            return self.options[self.selected_index]
        return None
        
    def _get_dropdown_rect(self) -> pygame.Rect:
        """Get the rectangle for the dropdown area"""
        abs_x, abs_y = self.get_absolute_position()
        items_to_show = min(len(self.options), self.max_visible_items)
        return pygame.Rect(abs_x, abs_y + self.height,
                         self.width, self.item_height * items_to_show)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle select events"""
        if not self.enabled or not self.visible:
            return False
            
        abs_x, abs_y = self.get_absolute_position()
        main_rect = pygame.Rect(abs_x, abs_y, self.width, self.height)
        
        # Handle mouse events
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if clicked on main select area
            if main_rect.collidepoint(event.pos):
                self.dropdown_open = not self.dropdown_open
                return True
                
            # Check if clicked on dropdown area
            if self.dropdown_open:
                dropdown_rect = self._get_dropdown_rect()
                if dropdown_rect.collidepoint(event.pos):
                    # Calculate which item was clicked
                    rel_y = event.pos[1] - dropdown_rect.y
                    clicked_index = rel_y // self.item_height
                    if 0 <= clicked_index < len(self.options):
                        self.selected_index = clicked_index
                        if self.on_selection_changed:
                            self.on_selection_changed(self.selected_index, self.options[self.selected_index])
                    self.dropdown_open = False
                    return True
                else:
                    # Click outside closes dropdown
                    self.dropdown_open = False
                    return True
                    
        elif event.type == pygame.MOUSEMOTION and self.dropdown_open:
            # Update hover index
            dropdown_rect = self._get_dropdown_rect()
            if dropdown_rect.collidepoint(event.pos):
                rel_y = event.pos[1] - dropdown_rect.y
                self.hover_index = rel_y // self.item_height
                if self.hover_index >= len(self.options):
                    self.hover_index = -1
            else:
                self.hover_index = -1
            return True
            
        # Handle keyboard events when focused
        elif event.type == pygame.KEYDOWN and self.dropdown_open:
            if event.key == pygame.K_UP:
                self.hover_index = max(0, self.hover_index - 1)
                return True
            elif event.key == pygame.K_DOWN:
                self.hover_index = min(len(self.options) - 1, self.hover_index + 1)
                return True
            elif event.key == pygame.K_RETURN:
                if 0 <= self.hover_index < len(self.options):
                    self.selected_index = self.hover_index
                    if self.on_selection_changed:
                        self.on_selection_changed(self.selected_index, self.options[self.selected_index])
                    self.dropdown_open = False
                return True
            elif event.key == pygame.K_ESCAPE:
                self.dropdown_open = False
                return True
                
        return False
        
    def render(self, screen: pygame.Surface):
        """Render the select component"""
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        
        # Draw main select area
        pygame.draw.rect(screen, self.background_color,
                        (abs_x, abs_y, self.width, self.height))
        
        # Draw selected text
        if self.selected_index >= 0:
            text_surface = self.font.render(self.options[self.selected_index], True, self.text_color)
            text_y = abs_y + (self.height - text_surface.get_height()) // 2
            screen.blit(text_surface, (abs_x + self.padding, text_y))
        
        # Draw arrow
        arrow_x = abs_x + self.width - self.arrow_size - self.padding
        arrow_y = abs_y + (self.height - self.arrow_size) // 2
        if self.dropdown_open:
            # Up arrow
            points = [(arrow_x, arrow_y + self.arrow_size),
                     (arrow_x + self.arrow_size, arrow_y + self.arrow_size),
                     (arrow_x + self.arrow_size // 2, arrow_y)]
        else:
            # Down arrow
            points = [(arrow_x, arrow_y),
                     (arrow_x + self.arrow_size, arrow_y),
                     (arrow_x + self.arrow_size // 2, arrow_y + self.arrow_size)]
        pygame.draw.polygon(screen, self.arrow_color, points)
        
        # Draw border
        pygame.draw.rect(screen, self.border_color,
                        (abs_x, abs_y, self.width, self.height),
                        self.border_width)
        
        # Draw dropdown if open
        if self.dropdown_open and self.options:
            dropdown_rect = self._get_dropdown_rect()
            
            # Draw dropdown background
            pygame.draw.rect(screen, self.background_color, dropdown_rect)
            
            # Draw options
            for i, option in enumerate(self.options[:self.max_visible_items]):
                item_rect = pygame.Rect(dropdown_rect.x,
                                      dropdown_rect.y + i * self.item_height,
                                      dropdown_rect.width,
                                      self.item_height)
                
                # Draw item background
                if i == self.hover_index:
                    pygame.draw.rect(screen, self.hover_color, item_rect)
                elif i == self.selected_index:
                    pygame.draw.rect(screen, self.selected_color, item_rect)
                
                # Draw item text
                text_surface = self.font.render(option, True, self.text_color)
                text_y = item_rect.y + (self.item_height - text_surface.get_height()) // 2
                screen.blit(text_surface, (item_rect.x + self.padding, text_y))
            
            # Draw dropdown border
            pygame.draw.rect(screen, self.border_color, dropdown_rect, self.border_width)
