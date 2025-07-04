"""
Code Viewer Scene - Displays source code of examples
"""

import pygame
import os
from pathlib import Path
from typing import List, Optional
from engine import BaseScene, Entity, Component
from components.menu_component import MenuButton

class CodeDisplay(Component):
    """Component for displaying syntax-highlighted code."""
    
    def __init__(self, width: int, height: int):
        super().__init__()
        self.width = width
        self.height = height
        self.scroll_y = 0
        self.max_scroll = 0
        self.scroll_speed = 300
        
        # Code content
        self.lines: List[str] = []
        self.line_height = 18
        self.font = None
        self.small_font = None
        
        # Syntax highlighting colors
        self.colors = {
            'background': (25, 25, 35),
            'text': (220, 220, 220),
            'keyword': (150, 200, 255),
            'string': (180, 255, 180),
            'comment': (150, 150, 150),
            'number': (255, 200, 150),
            'function': (255, 255, 150),
            'line_number': (100, 100, 120),
            'selection': (60, 80, 120)
        }
        
        # Python keywords for syntax highlighting
        self.keywords = {
            'def', 'class', 'if', 'else', 'elif', 'for', 'while', 'try', 'except',
            'import', 'from', 'return', 'yield', 'lambda', 'with', 'as', 'pass',
            'break', 'continue', 'and', 'or', 'not', 'in', 'is', 'True', 'False',
            'None', 'self', 'super', '__init__'
        }
        
    def set_code(self, code_text: str):
        """Set the code content to display."""
        self.lines = code_text.split('\n')
        self.scroll_y = 0
        
        # Calculate max scroll
        visible_lines = (self.height - 40) // self.line_height
        self.max_scroll = max(0, (len(self.lines) - visible_lines) * self.line_height)
        
    def update(self):
        if not self.entity:
            return
            
        # Initialize fonts if needed
        if not self.font:
            pygame.font.init()
            self.font = pygame.font.Font(None, 16)
            self.small_font = pygame.font.Font(None, 14)
            
        # Handle scrolling
        keys = pygame.key.get_pressed()
        dt = self.entity.delta_time
        
        if keys[pygame.K_UP]:
            self.scroll_y = max(0, self.scroll_y - self.scroll_speed * dt)
        elif keys[pygame.K_DOWN]:
            self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed * dt)
        elif keys[pygame.K_PAGEUP]:
            self.scroll_y = max(0, self.scroll_y - self.height * 0.8)
        elif keys[pygame.K_PAGEDOWN]:
            self.scroll_y = min(self.max_scroll, self.scroll_y + self.height * 0.8)
        elif keys[pygame.K_HOME]:
            self.scroll_y = 0
        elif keys[pygame.K_END]:
            self.scroll_y = self.max_scroll
            
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEWHEEL:
            # Mouse wheel scrolling
            self.scroll_y = max(0, min(self.max_scroll, self.scroll_y - event.y * 40))
            
    def render(self, screen: pygame.Surface, camera_offset=(0, 0)):
        if not self.entity or not self.font:
            return
            
        x = int(self.entity.position.x)
        y = int(self.entity.position.y)
        
        # Draw background
        background_rect = pygame.Rect(x, y, self.width, self.height)
        pygame.draw.rect(screen, self.colors['background'], background_rect)
        pygame.draw.rect(screen, (60, 60, 80), background_rect, 2)
        
        # Calculate visible area
        margin = 10
        content_rect = pygame.Rect(x + margin, y + margin, 
                                 self.width - 2 * margin, self.height - 2 * margin)
        
        # Set clipping region
        screen.set_clip(content_rect)
        
        # Calculate visible lines
        start_line = max(0, int(self.scroll_y // self.line_height))
        visible_lines = int(content_rect.height // self.line_height) + 2
        end_line = min(len(self.lines), start_line + visible_lines)
        
        # Draw line numbers background
        line_num_width = 50
        line_bg_rect = pygame.Rect(content_rect.x, content_rect.y, 
                                  line_num_width, content_rect.height)
        pygame.draw.rect(screen, (35, 35, 45), line_bg_rect)
        pygame.draw.line(screen, (60, 60, 80), 
                        (content_rect.x + line_num_width, content_rect.y),
                        (content_rect.x + line_num_width, content_rect.y + content_rect.height))
        
        # Draw code lines
        for line_idx in range(start_line, end_line):
            line_y = content_rect.y + (line_idx * self.line_height) - self.scroll_y
            
            if line_y > content_rect.bottom:
                break
                
            # Draw line number
            line_num_text = str(line_idx + 1).rjust(3)
            line_num_surface = self.small_font.render(line_num_text, True, self.colors['line_number'])
            screen.blit(line_num_surface, (content_rect.x + 5, line_y))
            
            # Draw code line with syntax highlighting
            if line_idx < len(self.lines):
                self._draw_highlighted_line(screen, self.lines[line_idx], 
                                          content_rect.x + line_num_width + 10, line_y)
        
        # Remove clipping
        screen.set_clip(None)
        
        # Draw scrollbar
        self._draw_scrollbar(screen, background_rect)
        
    def _draw_highlighted_line(self, screen: pygame.Surface, line: str, x: int, y: int):
        """Draw a line with syntax highlighting."""
        if not line.strip():
            return
            
        current_x = x
        i = 0
        
        while i < len(line):
            char = line[i]
            
            # Skip leading whitespace
            if char == ' ' or char == '\t':
                space_surface = self.font.render(char, True, self.colors['text'])
                screen.blit(space_surface, (current_x, y))
                current_x += space_surface.get_width()
                i += 1
                continue
            
            # Comments
            if char == '#':
                comment_text = line[i:]
                comment_surface = self.font.render(comment_text, True, self.colors['comment'])
                screen.blit(comment_surface, (current_x, y))
                break
                
            # Strings
            elif char in ['"', "'"]:
                quote = char
                string_start = i
                i += 1
                while i < len(line) and line[i] != quote:
                    if line[i] == '\\' and i + 1 < len(line):
                        i += 2  # Skip escaped character
                    else:
                        i += 1
                if i < len(line):
                    i += 1  # Include closing quote
                    
                string_text = line[string_start:i]
                string_surface = self.font.render(string_text, True, self.colors['string'])
                screen.blit(string_surface, (current_x, y))
                current_x += string_surface.get_width()
                continue
                
            # Numbers
            elif char.isdigit():
                num_start = i
                while i < len(line) and (line[i].isdigit() or line[i] == '.'):
                    i += 1
                    
                num_text = line[num_start:i]
                num_surface = self.font.render(num_text, True, self.colors['number'])
                screen.blit(num_surface, (current_x, y))
                current_x += num_surface.get_width()
                continue
                
            # Keywords and identifiers
            elif char.isalpha() or char == '_':
                word_start = i
                while i < len(line) and (line[i].isalnum() or line[i] == '_'):
                    i += 1
                    
                word = line[word_start:i]
                color = self.colors['keyword'] if word in self.keywords else self.colors['text']
                
                # Check for function definitions
                if word == 'def' and i < len(line):
                    # Highlight function name
                    word_surface = self.font.render(word, True, color)
                    screen.blit(word_surface, (current_x, y))
                    current_x += word_surface.get_width()
                    
                    # Find function name
                    while i < len(line) and line[i] == ' ':
                        space_surface = self.font.render(' ', True, self.colors['text'])
                        screen.blit(space_surface, (current_x, y))
                        current_x += space_surface.get_width()
                        i += 1
                        
                    if i < len(line) and (line[i].isalpha() or line[i] == '_'):
                        func_start = i
                        while i < len(line) and (line[i].isalnum() or line[i] == '_'):
                            i += 1
                        func_name = line[func_start:i]
                        func_surface = self.font.render(func_name, True, self.colors['function'])
                        screen.blit(func_surface, (current_x, y))
                        current_x += func_surface.get_width()
                    continue
                else:
                    word_surface = self.font.render(word, True, color)
                    screen.blit(word_surface, (current_x, y))
                    current_x += word_surface.get_width()
                continue
                
            # Other characters
            else:
                char_surface = self.font.render(char, True, self.colors['text'])
                screen.blit(char_surface, (current_x, y))
                current_x += char_surface.get_width()
                i += 1
                
    def _draw_scrollbar(self, screen: pygame.Surface, rect: pygame.Rect):
        """Draw scrollbar indicator."""
        if self.max_scroll <= 0:
            return
            
        scrollbar_width = 10
        scrollbar_x = rect.right - scrollbar_width - 5
        scrollbar_rect = pygame.Rect(scrollbar_x, rect.y + 5, scrollbar_width, rect.height - 10)
        
        # Scrollbar background
        pygame.draw.rect(screen, (40, 40, 50), scrollbar_rect)
        
        # Scrollbar thumb
        thumb_height = max(20, int((rect.height / (self.max_scroll + rect.height)) * scrollbar_rect.height))
        thumb_y = scrollbar_rect.y + int((self.scroll_y / self.max_scroll) * (scrollbar_rect.height - thumb_height))
        thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
        pygame.draw.rect(screen, (100, 100, 120), thumb_rect)

class CodeViewerScene(BaseScene):
    """Scene for viewing example source code."""
    
    def __init__(self, example_info, launcher):
        super().__init__()
        self.example_info = example_info
        self.launcher = launcher
        self.font = None
        self.title_font = None
        
        # File browser state
        self.current_file = None
        self.project_files: List[str] = []
        self.selected_file_index = 0
        
    def on_initialize(self):
        """Initialize the code viewer scene."""
        pygame.font.init()
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)
        
        # Discover project files
        self._discover_project_files()
        
        # Create UI elements
        self._create_ui_elements()
        
        # Load initial file
        if self.project_files:
            self._load_file(self.project_files[0])
            
    def _discover_project_files(self):
        """Discover all Python files in the example project."""
        example_path = self.launcher.base_path / self.example_info.file_path
        project_dir = example_path.parent
        
        self.project_files = []
        
        # Add main file first
        if example_path.exists():
            self.project_files.append(str(example_path.relative_to(project_dir)))
            
        # Discover other Python files
        for root, dirs, files in os.walk(project_dir):
            # Skip hidden directories and __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.endswith('.py') and file != example_path.name:
                    rel_path = Path(root).relative_to(project_dir) / file
                    self.project_files.append(str(rel_path))
                    
        # Also include README files
        for file in ['README.md', 'README.txt', 'readme.md']:
            readme_path = project_dir / file
            if readme_path.exists():
                self.project_files.append(file)
                
        self.project_files.sort()
        
    def _create_ui_elements(self):
        """Create UI elements for the code viewer."""
        # Back button
        back_button = Entity(100, 50)
        back_btn = MenuButton(
            text="← Back to Menu",
            width=150,
            height=40,
            callback=self._go_back,
            color=(80, 80, 100),
            hover_color=(100, 100, 130)
        )
        back_button.add_component(back_btn)
        self.add_entity(back_button, "ui")
        
        # Launch button
        launch_button = Entity(300, 50)
        launch_btn = MenuButton(
            text="▶ Launch Example",
            width=150,
            height=40,
            callback=self._launch_example,
            color=(50, 150, 50),
            hover_color=(70, 180, 70)
        )
        launch_button.add_component(launch_btn)
        self.add_entity(launch_button, "ui")
        
        # Code display
        code_display = Entity(600, 300)
        self.code_component = CodeDisplay(width=1000, height=500)
        code_display.add_component(self.code_component)
        self.add_entity(code_display, "ui")
        
    def _load_file(self, file_path: str):
        """Load and display a file."""
        self.current_file = file_path
        
        try:
            example_path = self.launcher.base_path / self.example_info.file_path
            project_dir = example_path.parent
            full_path = project_dir / file_path
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            self.code_component.set_code(content)
            
        except Exception as e:
            error_content = f"Error loading file: {file_path}\n\n{str(e)}"
            self.code_component.set_code(error_content)
            
    def _go_back(self):
        """Return to main menu."""
        if hasattr(self, 'interface') and self.interface:
            # Switch back to main menu scene
            from scenes.main_menu_scene import MainMenuScene
            main_scene = MainMenuScene()
            self.interface.scene_manager.add_scene("main_menu", main_scene)
            self.interface.scene_manager.set_scene("main_menu")
            
    def _launch_example(self):
        """Launch the example."""
        success = self.launcher.launch_example(self.example_info.name)
        if success:
            print(f"✓ {self.example_info.name} launched successfully")
        else:
            print(f"✗ Failed to launch {self.example_info.name}")
            
    def update(self, delta_time: float):
        """Update the code viewer scene."""
        super().update(delta_time)
        
    def render(self, screen: pygame.Surface):
        """Render the code viewer scene."""
        # Dark background
        screen.fill((20, 20, 25))
        
        # Title area
        title_text = f"Code Viewer - {self.example_info.name}"
        title_surface = self.title_font.render(title_text, True, (255, 255, 255))
        screen.blit(title_surface, (20, 20))
        
        # Example info
        info_text = f"Category: {self.example_info.category} | Difficulty: {self.example_info.difficulty}"
        info_surface = self.font.render(info_text, True, (200, 200, 200))
        screen.blit(info_surface, (20, 55))
        
        # File browser sidebar
        self._render_file_browser(screen)
        
        # Current file indicator
        if self.current_file:
            file_text = f"Current file: {self.current_file}"
            file_surface = self.font.render(file_text, True, (150, 200, 255))
            screen.blit(file_surface, (200, 100))
            
        # Render UI elements
        super().render(screen)
        
        # Instructions
        self._render_instructions(screen)
        
    def _render_file_browser(self, screen: pygame.Surface):
        """Render file browser sidebar."""
        sidebar_rect = pygame.Rect(20, 130, 150, 400)
        pygame.draw.rect(screen, (30, 30, 40), sidebar_rect)
        pygame.draw.rect(screen, (60, 60, 80), sidebar_rect, 2)
        
        # Files list
        y_offset = sidebar_rect.y + 10
        for i, file_path in enumerate(self.project_files):
            if y_offset > sidebar_rect.bottom - 20:
                break
                
            color = (100, 150, 255) if file_path == self.current_file else (200, 200, 200)
            
            # Truncate long filenames
            display_name = file_path
            if len(display_name) > 18:
                display_name = "..." + display_name[-15:]
                
            file_surface = self.font.render(display_name, True, color)
            screen.blit(file_surface, (sidebar_rect.x + 5, y_offset))
            
            y_offset += 25
            
    def _render_instructions(self, screen: pygame.Surface):
        """Render instructions."""
        instructions = [
            "Navigation:",
            "• Click files in sidebar to view",
            "• Mouse wheel or ↑/↓ to scroll",
            "• Page Up/Down for fast scroll",
            "• Home/End to go to top/bottom"
        ]
        
        y_start = 600
        for i, instruction in enumerate(instructions):
            color = (255, 255, 255) if i == 0 else (180, 180, 180)
            text_surface = self.font.render(instruction, True, color)
            screen.blit(text_surface, (200, y_start + i * 25))
            
    def handle_event(self, event: pygame.event.Event):
        """Handle events for code viewer."""
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._go_back()
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check if clicked on file browser
                mouse_x, mouse_y = event.pos
                if 20 <= mouse_x <= 170 and 140 <= mouse_y <= 530:
                    # Calculate which file was clicked
                    file_index = (mouse_y - 140) // 25
                    if 0 <= file_index < len(self.project_files):
                        self._load_file(self.project_files[file_index])