import pygame
from typing import List, Dict, Optional, Callable, Any, Tuple
from .ui_element import UIElement
from .panel import Panel
from .label import Label
from .button import Button

class GridColumn:
    def __init__(self, name: str, field: str, width: int,
                 sortable: bool = True,
                 formatter: Optional[Callable[[Any], str]] = None):
        self.name = name
        self.field = field
        self.width = width
        self.sortable = sortable
        self.formatter = formatter or str
        self.sort_direction: Optional[bool] = None  # True for asc, False for desc

class GridHeader(Panel):
    """Header panel with column headers"""
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)
        self.background_color = (240, 240, 240)
        self.border_color = (200, 200, 200)
        self.border_width = 1

class GridHeaderCell(Button):
    """Header cell with sorting capability"""
    def __init__(self, x: int, y: int, width: int, height: int,
                 column: GridColumn):
        super().__init__(x, y, width, height, column.name)
        self.column = column
        self.background_color = None
        self.hover_color = (220, 220, 220)
        self.text_color = (0, 0, 0)
        self.arrow_color = (100, 100, 100)
        self.padding = 8
    
    def render(self, screen: pygame.Surface):
        """Render header cell with sort arrow"""
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        
        # Background
        if self.hovered and self.enabled and self.column.sortable:
            color = self.hover_color
        else:
            color = self.background_color or (240, 240, 240)
            
        pygame.draw.rect(screen, color,
                        (abs_x, abs_y, self.width, self.height))
        
        # Text
        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_x = abs_x + self.padding
            text_y = abs_y + (self.height - text_surface.get_height()) // 2
            screen.blit(text_surface, (text_x, text_y))
        
        # Sort arrow
        if self.column.sort_direction is not None:
            arrow_size = 8
            arrow_x = abs_x + self.width - arrow_size - self.padding
            arrow_y = abs_y + (self.height - arrow_size) // 2
            
            if self.column.sort_direction:  # Ascending
                points = [
                    (arrow_x, arrow_y + arrow_size),
                    (arrow_x + arrow_size, arrow_y + arrow_size),
                    (arrow_x + arrow_size // 2, arrow_y)
                ]
            else:  # Descending
                points = [
                    (arrow_x, arrow_y),
                    (arrow_x + arrow_size, arrow_y),
                    (arrow_x + arrow_size // 2, arrow_y + arrow_size)
                ]
            
            pygame.draw.polygon(screen, self.arrow_color, points)

class GridRow(Panel):
    """Row panel containing cells"""
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)
        self.background_color = (255, 255, 255)
        self.hover_color = (245, 245, 245)
        self.selected_color = (230, 240, 255)
        self.border_color = (220, 220, 220)
        self.border_width = 1
        self._hovering = False
        self.selected = False
    
    def render(self, screen: pygame.Surface):
        """Render row with hover and selection effects"""
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        
        # Background
        if self.selected:
            color = self.selected_color
        elif self._hovering:
            color = self.hover_color
        else:
            color = self.background_color
            
        pygame.draw.rect(screen, color,
                        (abs_x, abs_y, self.width, self.height))
        
        # Border
        if self.border_color and self.border_width > 0:
            pygame.draw.line(screen, self.border_color,
                           (abs_x, abs_y + self.height - 1),
                           (abs_x + self.width, abs_y + self.height - 1),
                           self.border_width)
        
        # Render cells
        for child in self.children:
            child.render(screen)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle row hover and selection"""
        if not self.enabled or not self.visible:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            self._hovering = self.contains_point(*event.pos)
            
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.contains_point(*event.pos):
                self.selected = not self.selected
                return True
                
        return False

class Grid(UIElement):
    def __init__(self, x: int, y: int, width: int, height: int,
                 columns: List[GridColumn]):
        super().__init__(x, y, width, height)
        
        self.columns = columns
        self.row_height = 30
        self.header_height = 40
        self.data: List[Dict[str, Any]] = []
        
        # Create header
        self.header = GridHeader(0, 0, width, self.header_height)
        self.add_child(self.header)
        
        # Create header cells
        x = 0
        for column in columns:
            cell = GridHeaderCell(x, 0, column.width, self.header_height, column)
            if column.sortable:
                cell.on_click = lambda col=column: self._sort_by_column(col)
            self.header.add_child(cell)
            x += column.width
        
        # Create content panel
        self.content = Panel(0, self.header_height,
                           width, height - self.header_height)
        self.content.background_color = (255, 255, 255)
        self.add_child(self.content)
        
        # Selection
        self.selected_rows: List[int] = []
        self.on_selection_changed: Optional[Callable[[List[int]], None]] = None
    
    def set_data(self, data: List[Dict[str, Any]]):
        """Set grid data and refresh display"""
        self.data = data
        self._refresh_rows()
    
    def _refresh_rows(self):
        """Rebuild row display"""
        self.content.children.clear()
        y = 0
        
        for i, item in enumerate(self.data):
            row = GridRow(0, y, self.width, self.row_height)
            
            # Create cells
            x = 0
            for column in self.columns:
                value = item.get(column.field, '')
                text = column.formatter(value)
                
                label = Label(x + 8, 0, text)
                label.height = self.row_height
                row.add_child(label)
                
                x += column.width
            
            self.content.add_child(row)
            y += self.row_height
    
    def _sort_by_column(self, column: GridColumn):
        """Sort data by column"""
        if not column.sortable:
            return
            
        # Toggle sort direction
        if column.sort_direction is None:
            column.sort_direction = True  # Ascending
        else:
            column.sort_direction = not column.sort_direction
            
        # Clear other columns' sort direction
        for other in self.columns:
            if other != column:
                other.sort_direction = None
        
        # Sort data
        reverse = not column.sort_direction
        self.data.sort(key=lambda x: x.get(column.field, ''),
                      reverse=reverse)
        
        # Refresh display
        self._refresh_rows()
    
    def get_selected_data(self) -> List[Dict[str, Any]]:
        """Get data for selected rows"""
        return [self.data[i] for i in self.selected_rows]
