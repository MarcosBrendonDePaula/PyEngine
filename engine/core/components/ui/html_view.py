import pygame
from typing import List, Dict, Tuple, Optional
from .ui_element import UIElement
from .label import Label
import html

class CSSStyle:
    def __init__(self):
        self.color = None  # text color
        self.background_color = None
        self.font_size = None
        self.font_family = None
        self.margin = (0, 0, 0, 0)  # top, right, bottom, left
        self.padding = (0, 0, 0, 0)  # top, right, bottom, left
        self.text_align = 'left'  # left, center, right
        self.display = 'block'  # block, inline
        
    @staticmethod
    def parse_color(value: str) -> Optional[Tuple[int, int, int]]:
        """Parse CSS color value"""
        if value.startswith('#'):
            # Hex color
            try:
                if len(value) == 4:  # #RGB
                    r = int(value[1] + value[1], 16)
                    g = int(value[2] + value[2], 16)
                    b = int(value[3] + value[3], 16)
                    return (r, g, b)
                elif len(value) == 7:  # #RRGGBB
                    r = int(value[1:3], 16)
                    g = int(value[3:5], 16)
                    b = int(value[5:7], 16)
                    return (r, g, b)
            except ValueError:
                return None
        return None

class HTMLElement:
    def __init__(self, tag: str, content: str = "", attributes: Dict[str, str] = None):
        self.tag = tag
        self.content = content
        self.attributes = attributes or {}
        self.children: List[HTMLElement] = []
        self.parent: Optional[HTMLElement] = None
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.style = CSSStyle()
        
        # Parse inline style if present
        if 'style' in self.attributes:
            self._parse_inline_style(self.attributes['style'])
        
    def _parse_inline_style(self, style_str: str):
        """Parse inline CSS style string"""
        declarations = [s.strip() for s in style_str.split(';') if s.strip()]
        for declaration in declarations:
            if ':' not in declaration:
                continue
            property_name, value = declaration.split(':', 1)
            property_name = property_name.strip()
            value = value.strip()
            
            if property_name == 'color':
                self.style.color = CSSStyle.parse_color(value)
            elif property_name == 'background-color':
                self.style.background_color = CSSStyle.parse_color(value)
            elif property_name == 'font-size':
                try:
                    if value.endswith('px'):
                        self.style.font_size = int(value[:-2])
                except ValueError:
                    pass
            elif property_name == 'text-align':
                if value in ['left', 'center', 'right']:
                    self.style.text_align = value
        
    def add_child(self, child: 'HTMLElement'):
        child.parent = self
        self.children.append(child)

class HTMLView(UIElement):
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)
        
        # Styling
        self.background_color = (255, 255, 255)
        self.text_color = (0, 0, 0)
        self.link_color = (0, 0, 255)
        self.default_font_size = 32
        self.font = pygame.font.Font(None, self.default_font_size)
        self.heading_sizes = {
            'h1': 48,
            'h2': 40,
            'h3': 36,
            'h4': 32,
            'h5': 28,
            'h6': 24
        }
        
        # Content
        self.root: Optional[HTMLElement] = None
        self.elements: List[HTMLElement] = []
        
        # Scroll state
        self.scroll_y = 0
        self.max_scroll = 0
        
    def set_html(self, html_content: str):
        """Parse and set HTML content"""
        # Normalize line endings and remove extra whitespace
        html_content = html_content.replace('\r\n', '\n').replace('\r', '\n')
        html_content = '\n'.join(line.strip() for line in html_content.split('\n'))
        self.root = self._parse_html(html_content)
        self._layout_elements()
        
    def _parse_html(self, html_content: str) -> HTMLElement:
        """Simple HTML parser - supports basic tags and CSS"""
        root = HTMLElement('root')
        current = root
        tag_stack = []
        
        # Simple state machine for parsing
        i = 0
        text_buffer = []
        
        def flush_text_buffer():
            nonlocal text_buffer
            if text_buffer:
                text = ' '.join(''.join(text_buffer).split())
                if text:
                    text = html.unescape(text)  # Decode HTML entities
                    element = HTMLElement('text', content=text)
                    current.add_child(element)
                text_buffer = []
        
        while i < len(html_content):
            if html_content[i] == '<':
                # Flush any pending text
                flush_text_buffer()
                
                if html_content[i+1] == '/':
                    # Closing tag
                    end = html_content.find('>', i)
                    if end != -1:
                        tag_name = html_content[i+2:end].strip().lower()
                        if tag_stack and tag_stack[-1].tag == tag_name:
                            current = tag_stack.pop().parent
                        i = end + 1
                        continue
                else:
                    # Opening tag
                    end = html_content.find('>', i)
                    if end != -1:
                        tag_content = html_content[i+1:end].strip()
                        parts = tag_content.split(' ', 1)
                        tag_name = parts[0].lower()
                        
                        # Parse attributes
                        attributes = {}
                        if len(parts) > 1:
                            attr_str = parts[1]
                            # Simple attribute parsing
                            while attr_str:
                                attr_str = attr_str.strip()
                                if not attr_str:
                                    break
                                    
                                # Find attribute name
                                eq_pos = attr_str.find('=')
                                if eq_pos == -1:
                                    break
                                    
                                attr_name = attr_str[:eq_pos].strip()
                                attr_str = attr_str[eq_pos+1:].strip()
                                
                                # Find attribute value
                                quote = attr_str[0]
                                if quote in '"\'':
                                    end_quote = attr_str.find(quote, 1)
                                    if end_quote == -1:
                                        break
                                    attr_value = attr_str[1:end_quote]
                                    attributes[attr_name] = attr_value
                                    attr_str = attr_str[end_quote+1:]
                        
                        # Create element
                        element = HTMLElement(tag_name, attributes=attributes)
                        current.add_child(element)
                        
                        # Self-closing tags
                        if tag_name not in ['br', 'img', 'hr']:
                            tag_stack.append(current)
                            current = element
                            
                        i = end + 1
                        continue
            else:
                # Collect text content
                text_buffer.append(html_content[i])
            i += 1
            
        # Flush any remaining text
        flush_text_buffer()
                
        return root
        
    def _layout_elements(self):
        """Layout HTML elements with word wrapping and CSS support"""
        self.elements.clear()
        if not self.root:
            return
            
        x = self.x + self.padding
        y = self.y + self.padding
        line_height = 0
        line_elements = []
        max_width = self.width - (self.padding * 2)
        
        def flush_line():
            nonlocal x, y, line_height, line_elements
            if not line_elements:
                return
                
            # Handle text alignment
            total_width = sum(elem.width + 5 for elem in line_elements) - 5
            if line_elements[0].parent and line_elements[0].parent.style.text_align == 'center':
                x_offset = (max_width - total_width) // 2
            elif line_elements[0].parent and line_elements[0].parent.style.text_align == 'right':
                x_offset = max_width - total_width
            else:
                x_offset = 0
                
            # Position elements on the line
            curr_x = self.x + self.padding + x_offset
            for elem in line_elements:
                elem.x = curr_x
                elem.y = y
                curr_x += elem.width + 5
            
            y += line_height + 5
            x = self.x + self.padding
            line_height = 0
            line_elements.clear()
        
        def layout_element(element: HTMLElement) -> None:
            nonlocal x, y, line_height
            
            if element.tag == 'text':
                # Get font based on parent's style
                font_size = element.parent.style.font_size if element.parent and element.parent.style.font_size else self.default_font_size
                font = pygame.font.Font(None, font_size)
                
                # Split text into words for better wrapping
                words = element.content.split()
                for word in words:
                    # Render word with current font
                    color = element.parent.style.color if element.parent and element.parent.style.color else self.text_color
                    text_surface = font.render(word, True, color)
                    word_element = HTMLElement('text', content=word)
                    word_element.width = text_surface.get_width()
                    word_element.height = text_surface.get_height()
                    
                    # Check if we need to wrap to next line
                    if x + word_element.width > self.x + max_width and line_elements:
                        flush_line()
                    
                    line_elements.append(word_element)
                    x += word_element.width + 5
                    line_height = max(line_height, word_element.height)
                    self.elements.append(word_element)
                
            elif element.tag in self.heading_sizes:
                flush_line()
                y += 10  # Add spacing before heading
                
                # Set heading style
                element.style.font_size = self.heading_sizes[element.tag]
                
                for child in element.children:
                    layout_element(child)
                    
                flush_line()
                y += 10  # Add spacing after heading
                
            elif element.tag == 'p':
                flush_line()
                y += 10  # Add spacing before paragraph
                
                for child in element.children:
                    layout_element(child)
                    
                flush_line()
                y += 10  # Add spacing after paragraph
                
            elif element.tag == 'br':
                flush_line()
                
            else:
                # Generic element - just layout children
                for child in element.children:
                    layout_element(child)
        
        # Layout all elements
        layout_element(self.root)
        flush_line()
        
        # Update max scroll
        self.max_scroll = max(0, y - (self.y + self.height))
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events"""
        if not self.enabled or not self.visible:
            return False
            
        if event.type == pygame.MOUSEWHEEL:
            # Scroll
            self.scroll_y = max(0, min(self.max_scroll, 
                                     self.scroll_y - event.y * 20))
            return True
            
        return False
        
    def render(self, screen: pygame.Surface):
        """Render HTML view with CSS styling"""
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        
        # Draw background
        pygame.draw.rect(screen, self.background_color,
                        (abs_x, abs_y, self.width, self.height))
        
        # Create a surface for content
        content_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Render elements
        for element in self.elements:
            if element.tag == 'text':
                # Get font based on parent's style
                font_size = element.parent.style.font_size if element.parent and element.parent.style.font_size else self.default_font_size
                font = pygame.font.Font(None, font_size)
                
                # Get text color from style
                color = element.parent.style.color if element.parent and element.parent.style.color else self.text_color
                
                # Render text
                text_surface = font.render(element.content, True, color)
                content_surface.blit(text_surface, 
                                   (element.x - self.x,
                                    element.y - self.y - self.scroll_y))
        
        # Draw content with clipping
        screen.blit(content_surface, (abs_x, abs_y))
        
        # Draw border
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(screen, self.border_color,
                           (abs_x, abs_y, self.width, self.height),
                           self.border_width)
