import pygame
from typing import List, Tuple, Optional, Callable
from .ui_element import UIElement
from .input import Input

class InputSelect(Input):
    def __init__(self, x: int, y: int, width: int, height: int, options: List[str] = None):
        super().__init__(x, y, width, height)
        
        # Options
        self.all_options = options or []
        self.filtered_options = self.all_options.copy()
        self.selected_index = -1
        self.dropdown_open = False
        self.hover_index = -1
        
        # Appearance
        self.item_height = 30
        self.max_visible_items = 5
        
        # Additional colors
        self.hover_color = (230, 230, 230)     # Light gray
        self.selected_color = (200, 200, 255)  # Light blue
        
        # Arrow indicator
        self.arrow_color = (100, 100, 100)
        self.arrow_size = 10
        
        # Event handlers
        self.on_selection_changed: Optional[Callable[[int, str], None]] = None
        
    def set_options(self, options: List[str]):
        """Set the list of options"""
        self.all_options = options
        self._filter_options()
        
    def _filter_options(self):
        """Filter options based on current input text"""
        if not self.text:
            self.filtered_options = self.all_options.copy()
        else:
            search_text = self.text.lower()
            self.filtered_options = [
                opt for opt in self.all_options
                if search_text in opt.lower()
            ]
        self.hover_index = -1
        
    def _get_dropdown_rect(self) -> pygame.Rect:
        """Get the rectangle for the dropdown area"""
        abs_x, abs_y = self.get_absolute_position()
        items_to_show = min(len(self.filtered_options), self.max_visible_items)
        return pygame.Rect(abs_x, abs_y + self.height,
                         self.width, self.item_height * items_to_show)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input and select events"""
        if not self.enabled or not self.visible:
            return False
            
        abs_x, abs_y = self.get_absolute_position()
        main_rect = pygame.Rect(abs_x, abs_y, self.width, self.height)
        
        # Handle text input and basic input events
        if super().handle_event(event):
            if event.type == pygame.TEXTINPUT or (
                event.type == pygame.KEYDOWN and 
                event.key in (pygame.K_BACKSPACE, pygame.K_DELETE)
            ):
                # Update filtered options when text changes
                self._filter_options()
                self.dropdown_open = True
            return True
            
        # Handle mouse events for dropdown
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if clicked on main area
            if main_rect.collidepoint(event.pos):
                self.dropdown_open = not self.dropdown_open
                return True
                
            # Check if clicked on dropdown area
            if self.dropdown_open and self.filtered_options:
                dropdown_rect = self._get_dropdown_rect()
                if dropdown_rect.collidepoint(event.pos):
                    # Calculate which item was clicked
                    rel_y = event.pos[1] - dropdown_rect.y
                    clicked_index = rel_y // self.item_height
                    if 0 <= clicked_index < len(self.filtered_options):
                        self.selected_index = clicked_index
                        self.text = self.filtered_options[clicked_index]
                        self.cursor_pos = len(self.text)
                        self.selection_start = None
                        if self.on_selection_changed:
                            self.on_selection_changed(self.selected_index, self.text)
                        if self.on_text_changed:
                            self.on_text_changed(self.text)
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
                if self.hover_index >= len(self.filtered_options):
                    self.hover_index = -1
            else:
                self.hover_index = -1
            return True
            
        # Handle keyboard navigation in dropdown
        elif event.type == pygame.KEYDOWN and self.dropdown_open:
            if event.key == pygame.K_UP:
                self.hover_index = max(0, self.hover_index - 1)
                return True
            elif event.key == pygame.K_DOWN:
                self.hover_index = min(len(self.filtered_options) - 1,
                                     self.hover_index + 1 if self.hover_index >= 0 else 0)
                return True
            elif event.key == pygame.K_RETURN:
                if 0 <= self.hover_index < len(self.filtered_options):
                    self.selected_index = self.hover_index
                    self.text = self.filtered_options[self.hover_index]
                    self.cursor_pos = len(self.text)
                    self.selection_start = None
                    if self.on_selection_changed:
                        self.on_selection_changed(self.selected_index, self.text)
                    if self.on_text_changed:
                        self.on_text_changed(self.text)
                    self.dropdown_open = False
                return True
            elif event.key == pygame.K_ESCAPE:
                self.dropdown_open = False
                return True
                
        return False
        
    def render(self, screen: pygame.Surface):
        """Render the input select component"""
        if not self.visible:
            return
            
        # Draw input field
        super().render(screen)
        
        abs_x, abs_y = self.get_absolute_position()
        
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
        
        # Draw dropdown if open
        if self.dropdown_open and self.filtered_options:
            dropdown_rect = self._get_dropdown_rect()
            
            # Draw dropdown background
            pygame.draw.rect(screen, self.background_color, dropdown_rect)
            
            # Draw options
            for i, option in enumerate(self.filtered_options[:self.max_visible_items]):
                item_rect = pygame.Rect(dropdown_rect.x,
                                      dropdown_rect.y + i * self.item_height,
                                      dropdown_rect.width,
                                      self.item_height)
                
                # Draw item background
                if i == self.hover_index:
                    pygame.draw.rect(screen, self.hover_color, item_rect)
                elif option == self.text:
                    pygame.draw.rect(screen, self.selected_color, item_rect)
                
                # Draw item text
                text_surface = self.font.render(option, True, self.text_color)
                text_y = item_rect.y + (self.item_height - text_surface.get_height()) // 2
                screen.blit(text_surface, (item_rect.x + self.padding, text_y))
            
            # Draw dropdown border
            pygame.draw.rect(screen, self.border_color, dropdown_rect, self.border_width)
