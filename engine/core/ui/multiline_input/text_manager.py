from typing import List, Optional, Tuple, Callable

class TextManager:
    def __init__(self):
        self.lines: List[str] = [""]
        self.text = ""
        self.on_text_changed: Optional[Callable[[str], None]] = None
        
    def set_text(self, text: str):
        """Set the text content"""
        self.lines = text.split('\n')
        if not self.lines:
            self.lines = [""]
        self.text = text
        self._notify_change()
        
    def insert_text(self, position: int, text: str):
        """Insert text at specified position"""
        line, column = self._get_line_and_column(position)
        current_line = self.lines[line]
        self.lines[line] = current_line[:column] + text + current_line[column:]
        self._update_text()
        
    def delete_text(self, start: int, end: int):
        """Delete text between start and end positions"""
        if start < 0 or end > len(self.text) or start >= end:
            return False
            
        start_line, start_col = self._get_line_and_column(start)
        end_line, end_col = self._get_line_and_column(end)
        
        if start_line == end_line:
            # Delete within same line
            current_line = self.lines[start_line]
            self.lines[start_line] = current_line[:start_col] + current_line[end_col:]
        else:
            # Delete across multiple lines
            first_line = self.lines[start_line][:start_col]
            last_line = self.lines[end_line][end_col:]
            self.lines[start_line] = first_line + last_line
            del self.lines[start_line + 1:end_line + 1]
            
        # Ensure at least one empty line exists
        if not self.lines:
            self.lines = [""]
            
        self._update_text()
        return True
        
    def insert_newline(self, position: int):
        """Insert a new line at specified position"""
        line, column = self._get_line_and_column(position)
        current_line = self.lines[line]
        self.lines[line] = current_line[:column]
        self.lines.insert(line + 1, current_line[column:])
        self._update_text()
        
    def merge_lines(self, line: int):
        """Merge a line with the previous line"""
        if line > 0 and line < len(self.lines):
            self.lines[line - 1] += self.lines[line]
            self.lines.pop(line)
            self._update_text()
            
    def get_line_start_position(self, line: int) -> int:
        """Get the absolute position of the start of a line"""
        pos = 0
        for i in range(line):
            pos += len(self.lines[i]) + 1  # +1 for newline
        return pos
        
    def get_line_end_position(self, line: int) -> int:
        """Get the absolute position of the end of a line"""
        return self.get_line_start_position(line) + len(self.lines[line])
        
    def _get_line_and_column(self, position: int) -> Tuple[int, int]:
        """Convert absolute position to line and column"""
        line = 0
        remaining_pos = position
        
        for text in self.lines:
            if remaining_pos <= len(text):
                return line, remaining_pos
            remaining_pos -= len(text) + 1  # +1 for newline
            line += 1
        
        return len(self.lines) - 1, len(self.lines[-1])
        
    def _update_text(self):
        """Update text property from lines"""
        self.text = '\n'.join(self.lines)
        self._notify_change()
        
    def _notify_change(self):
        """Notify text changed"""
        if self.on_text_changed:
            self.on_text_changed(self.text)
