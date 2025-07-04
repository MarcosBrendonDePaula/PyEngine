import pygame
from typing import List, Tuple, Optional
from ..component import Component

class LogMessage:
    def __init__(self, text: str, level: str = "info", duration: Optional[float] = None):
        self.text = text
        self.level = level  # "info", "warning", "error"
        self.duration = duration  # None means permanent
        self.creation_time = pygame.time.get_ticks()
        
    def should_remove(self) -> bool:
        if self.duration is None:
            return False
        return pygame.time.get_ticks() - self.creation_time > self.duration * 1000

class LogComponent(Component):
    def __init__(self, max_messages: int = 5, font_size: int = 16):
        super().__init__()
        
        # Initialize pygame font if not already initialized
        if not pygame.font.get_init():
            pygame.font.init()
            
        self.font = pygame.font.Font(None, font_size)
        self.max_messages = max_messages
        self.messages: List[LogMessage] = []
        
        # Visual settings
        self.line_height = font_size + 4
        self.padding = 5
        self.colors = {
            "info": (255, 255, 255),     # White
            "warning": (255, 255, 0),     # Yellow
            "error": (255, 0, 0)          # Red
        }
        self.background_alpha = 128
        
    def log(self, text: str, level: str = "info", duration: Optional[float] = None):
        """Add a new log message
        
        Args:
            text: The message text
            level: Message level ("info", "warning", "error")
            duration: How long to show the message in seconds (None for permanent)
        """
        self.messages.append(LogMessage(text, level, duration))
        # Remove oldest messages if exceeding max_messages
        while len(self.messages) > self.max_messages:
            self.messages.pop(0)
            
    def clear(self):
        """Clear all log messages"""
        self.messages.clear()
            
    def update(self):
        """Update log messages, removing expired ones"""
        # Remove expired messages
        self.messages = [msg for msg in self.messages if not msg.should_remove()]
            
    def render(self, screen: pygame.Surface, offset: Tuple[float, float] = (0, 0)):
        """Render log messages"""
        if not self.messages:
            return
            
        # Calculate total height needed
        total_height = len(self.messages) * self.line_height + (self.padding * 2)
        
        # Create semi-transparent background surface
        background = pygame.Surface((screen.get_width(), total_height), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        
        # Get entity position
        x = self.entity.position.x + offset[0] if self.entity else 0
        y = self.entity.position.y + offset[1] if self.entity else 0
        
        # Draw background
        screen.blit(background, (x, y))
        
        # Draw messages
        current_y = y + self.padding
        for msg in self.messages:
            try:
                text_surface = self.font.render(msg.text, True, self.colors[msg.level])
                screen.blit(text_surface, (x + self.padding, current_y))
                current_y += self.line_height
            except pygame.error as e:
                print(f"Error rendering log message: {e}")
                print(f"Message: {msg.text}")
                
    def get_messages(self) -> List[LogMessage]:
        """Get current log messages"""
        return self.messages.copy()
