from typing import Tuple, List

class Cursor:
    def __init__(self):
        self.position = 0
        self.selection_start = None
        
    def get_position_in_lines(self, lines: List[str]) -> Tuple[int, int]:
        """Get cursor position as (line, column)"""
        line = 0
        remaining_pos = self.position
        
        for text in lines:
            if remaining_pos <= len(text):
                return line, remaining_pos
            remaining_pos -= len(text) + 1  # +1 for newline
            line += 1
        
        # If cursor is beyond text, place it at the end of the last line
        return len(lines) - 1, len(lines[-1])
        
    def get_absolute_position(self, lines: List[str], line: int, column: int) -> int:
        """Convert line and column to absolute cursor position"""
        pos = 0
        for i in range(line):
            pos += len(lines[i]) + 1  # +1 for newline
        return pos + min(column, len(lines[line]))  # Ensure column doesn't exceed line length
        
    def move_left(self, text_length: int) -> bool:
        """Move cursor left one position"""
        if self.position > 0:
            self.position -= 1
            return True
        return False
        
    def move_right(self, text_length: int) -> bool:
        """Move cursor right one position"""
        if self.position < text_length:
            self.position += 1
            return True
        return False
        
    def move_up(self, lines: List[str]) -> bool:
        """Move cursor up one line"""
        line, column = self.get_position_in_lines(lines)
        if line > 0:
            # Keep horizontal position when moving up
            new_column = min(column, len(lines[line - 1]))
            self.position = self.get_absolute_position(lines, line - 1, new_column)
            return True
        return False
        
    def move_down(self, lines: List[str]) -> bool:
        """Move cursor down one line"""
        line, column = self.get_position_in_lines(lines)
        if line < len(lines) - 1:
            # Keep horizontal position when moving down
            new_column = min(column, len(lines[line + 1]))
            self.position = self.get_absolute_position(lines, line + 1, new_column)
            return True
        return False
        
    def set_position(self, position: int, text_length: int):
        """Set cursor position with bounds checking"""
        self.position = max(0, min(position, text_length))
        
    def move_to_line_start(self, lines: List[str]):
        """Move cursor to start of current line"""
        line, _ = self.get_position_in_lines(lines)
        self.position = self.get_absolute_position(lines, line, 0)
        
    def move_to_line_end(self, lines: List[str]):
        """Move cursor to end of current line"""
        line, _ = self.get_position_in_lines(lines)
        self.position = self.get_absolute_position(lines, line, len(lines[line]))
        
    def start_selection(self):
        """Start text selection from current cursor position"""
        self.selection_start = self.position
        
    def clear_selection(self):
        """Clear text selection"""
        self.selection_start = None
        
    def get_selection_range(self) -> Tuple[int, int]:
        """Get the start and end positions of selection"""
        if self.selection_start is None:
            return self.position, self.position
        return min(self.selection_start, self.position), max(self.selection_start, self.position)
