import pygame
from typing import Optional, Callable

class KeyHandler:
    def __init__(self):
        # Key repeat settings
        self.repeat_delay = 500  # ms before key starts repeating
        self.repeat_interval = 50  # ms between repeats
        self.backspace_interval = 30  # faster interval for backspace
        
        # State
        self.repeat_key: Optional[int] = None
        self.repeat_timer = 0
        self.last_key_time = 0
        
    def handle_key_down(self, event: pygame.event.Event, current_time: int) -> bool:
        """Handle key down event and determine if it should trigger a repeat"""
        # Reset key repeat timer on new key press
        if event.key != self.repeat_key:
            self.repeat_key = event.key
            self.repeat_timer = current_time
            self.last_key_time = current_time
            return True
        return False
        
    def handle_key_repeat(self, current_time: int, keys: list) -> bool:
        """Handle key repeat timing and return whether to trigger a repeat"""
        if self.repeat_key is not None:
            if current_time - self.repeat_timer >= self.repeat_delay:
                # Use faster interval for backspace
                interval = (self.backspace_interval 
                          if self.repeat_key == pygame.K_BACKSPACE 
                          else self.repeat_interval)
                
                if current_time - self.last_key_time >= interval:
                    if keys[self.repeat_key]:
                        self.last_key_time = current_time
                        return True
            else:
                if not keys[self.repeat_key]:
                    self.repeat_key = None
        return False
        
    def reset(self):
        """Reset key repeat state"""
        self.repeat_key = None
        self.repeat_timer = 0
        self.last_key_time = 0
        
    def is_repeating(self, key: int) -> bool:
        """Check if a specific key is currently repeating"""
        return self.repeat_key == key
