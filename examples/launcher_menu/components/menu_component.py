"""
Menu components for the launcher
"""

import pygame
import math
from engine import Component
from typing import List, Callable, Optional, Tuple

class MenuButton(Component):
    """Interactive menu button component."""
    
    def __init__(self, 
                 text: str,
                 width: int = 200,
                 height: int = 50,
                 callback: Optional[Callable] = None,
                 color: Tuple[int, int, int] = (70, 130, 180),
                 hover_color: Tuple[int, int, int] = (100, 149, 237),
                 text_color: Tuple[int, int, int] = (255, 255, 255)):
        super().__init__()
        self.text = text
        self.width = width
        self.height = height
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        
        # State
        self.is_hovered = False
        self.is_pressed = False
        self.hover_scale = 1.0
        self.pulse_timer = 0.0
        
        # Font
        pygame.font.init()
        self.font = pygame.font.Font(None, 24)
        
    def update(self):
        if not self.entity:
            return
            
        dt = self.entity.delta_time
        
        # Update hover animation
        target_scale = 1.1 if self.is_hovered else 1.0
        self.hover_scale += (target_scale - self.hover_scale) * 8 * dt
        
        # Pulse effect
        self.pulse_timer += dt * 3
        
        # Check mouse position
        mouse_pos = pygame.mouse.get_pos()
        self._check_hover(mouse_pos)
        
    def _check_hover(self, mouse_pos: Tuple[int, int]):
        """Check if mouse is hovering over button."""
        if not self.entity:
            return
            
        x = self.entity.position.x - self.width // 2
        y = self.entity.position.y - self.height // 2
        
        self.is_hovered = (
            x <= mouse_pos[0] <= x + self.width and
            y <= mouse_pos[1] <= y + self.height
        )
        
    def render(self, screen: pygame.Surface, camera_offset=(0, 0)):
        if not self.entity:
            return
            
        # Calculate position and size with scaling
        scale = self.hover_scale
        scaled_width = int(self.width * scale)
        scaled_height = int(self.height * scale)
        
        x = int(self.entity.position.x - scaled_width // 2)
        y = int(self.entity.position.y - scaled_height // 2)
        
        # Choose color based on state
        if self.is_pressed:
            color = tuple(c - 30 for c in self.hover_color)
        elif self.is_hovered:
            # Add pulse effect when hovered
            pulse = 1.0 + 0.1 * math.sin(self.pulse_timer)
            color = tuple(int(c * pulse) for c in self.hover_color)
        else:
            color = self.color
            
        # Draw button background
        button_rect = pygame.Rect(x, y, scaled_width, scaled_height)
        pygame.draw.rect(screen, color, button_rect, border_radius=8)
        
        # Draw border
        border_color = (255, 255, 255) if self.is_hovered else (200, 200, 200)
        pygame.draw.rect(screen, border_color, button_rect, 2, border_radius=8)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect)
        
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:  # Left click
                self.is_pressed = True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_pressed and self.is_hovered:
                self.is_pressed = False
                if self.callback:
                    self.callback()
            else:
                self.is_pressed = False

class ExampleCard(Component):
    """Card component for displaying example information."""
    
    def __init__(self, example_info, width: int = 300, height: int = 200):
        super().__init__()
        self.example_info = example_info
        self.width = width
        self.height = height
        
        # State
        self.is_hovered = False
        self.hover_scale = 1.0
        self.glow_alpha = 0
        
        # Fonts
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 28)
        self.text_font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)
        
        # Colors
        self.bg_color = (45, 45, 55)
        self.border_color = (100, 100, 120)
        self.title_color = (255, 255, 255)
        self.text_color = (200, 200, 200)
        self.feature_color = (150, 200, 255)
        
        # Difficulty colors
        self.difficulty_colors = {
            "Beginner": (100, 200, 100),
            "Intermediate": (255, 200, 100),
            "Advanced": (255, 100, 100)
        }
        
    def update(self):
        if not self.entity:
            return
            
        dt = self.entity.delta_time
        
        # Update hover animation
        target_scale = 1.05 if self.is_hovered else 1.0
        self.hover_scale += (target_scale - self.hover_scale) * 6 * dt
        
        # Update glow effect
        target_glow = 100 if self.is_hovered else 0
        self.glow_alpha += (target_glow - self.glow_alpha) * 5 * dt
        
        # Check mouse hover
        mouse_pos = pygame.mouse.get_pos()
        self._check_hover(mouse_pos)
        
    def _check_hover(self, mouse_pos: Tuple[int, int]):
        """Check if mouse is hovering over card."""
        if not self.entity:
            return
            
        x = self.entity.position.x - self.width // 2
        y = self.entity.position.y - self.height // 2
        
        self.is_hovered = (
            x <= mouse_pos[0] <= x + self.width and
            y <= mouse_pos[1] <= y + self.height
        )
        
    def render(self, screen: pygame.Surface, camera_offset=(0, 0)):
        if not self.entity:
            return
            
        # Calculate scaled dimensions
        scale = self.hover_scale
        scaled_width = int(self.width * scale)
        scaled_height = int(self.height * scale)
        
        x = int(self.entity.position.x - scaled_width // 2)
        y = int(self.entity.position.y - scaled_height // 2)
        
        card_rect = pygame.Rect(x, y, scaled_width, scaled_height)
        
        # Draw glow effect
        if self.glow_alpha > 0:
            glow_surface = pygame.Surface((scaled_width + 20, scaled_height + 20))
            glow_surface.set_alpha(int(self.glow_alpha))
            glow_surface.fill((100, 150, 255))
            screen.blit(glow_surface, (x - 10, y - 10))
        
        # Draw card background
        pygame.draw.rect(screen, self.bg_color, card_rect, border_radius=12)
        
        # Draw border
        border_color = (150, 150, 200) if self.is_hovered else self.border_color
        pygame.draw.rect(screen, border_color, card_rect, 2, border_radius=12)
        
        # Draw content
        self._draw_content(screen, card_rect)
        
    def _draw_content(self, screen: pygame.Surface, rect: pygame.Rect):
        """Draw card content."""
        margin = 15
        y_offset = rect.top + margin
        
        # Title
        title_surface = self.title_font.render(self.example_info.name, True, self.title_color)
        title_rect = title_surface.get_rect(centerx=rect.centerx, y=y_offset)
        screen.blit(title_surface, title_rect)
        y_offset += 35
        
        # Difficulty badge
        difficulty_color = self.difficulty_colors.get(self.example_info.difficulty, (128, 128, 128))
        badge_rect = pygame.Rect(rect.left + margin, y_offset, 80, 20)
        pygame.draw.rect(screen, difficulty_color, badge_rect, border_radius=10)
        
        diff_text = self.small_font.render(self.example_info.difficulty, True, (255, 255, 255))
        diff_rect = diff_text.get_rect(center=badge_rect.center)
        screen.blit(diff_text, diff_rect)
        
        # Threading indicator
        if self.example_info.threading_demo:
            thread_rect = pygame.Rect(rect.right - margin - 60, y_offset, 60, 20)
            pygame.draw.rect(screen, (255, 100, 100), thread_rect, border_radius=10)
            thread_text = self.small_font.render("Threading", True, (255, 255, 255))
            thread_text_rect = thread_text.get_rect(center=thread_rect.center)
            screen.blit(thread_text, thread_text_rect)
        
        y_offset += 35
        
        # Description
        description = self._wrap_text(self.example_info.description, rect.width - 2 * margin)
        for line in description:
            text_surface = self.text_font.render(line, True, self.text_color)
            screen.blit(text_surface, (rect.left + margin, y_offset))
            y_offset += 22
            
        y_offset += 10
        
        # Features
        if self.example_info.features and y_offset < rect.bottom - 30:
            features_text = "Features: " + ", ".join(self.example_info.features[:3])
            if len(self.example_info.features) > 3:
                features_text += "..."
                
            features = self._wrap_text(features_text, rect.width - 2 * margin)
            for line in features:
                text_surface = self.small_font.render(line, True, self.feature_color)
                screen.blit(text_surface, (rect.left + margin, y_offset))
                y_offset += 18
                if y_offset >= rect.bottom - margin:
                    break
                    
    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if self.text_font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
                
        if current_line:
            lines.append(current_line)
            
        return lines
    
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:  # Left click
                # Card was clicked - could trigger launch or detail view
                return True
        return False

class ScrollableContainer(Component):
    """Container that can scroll through content."""
    
    def __init__(self, width: int, height: int, content_height: int):
        super().__init__()
        self.width = width
        self.height = height
        self.content_height = content_height
        self.scroll_y = 0
        self.max_scroll = max(0, content_height - height)
        self.scroll_speed = 50
        
    def update(self):
        if not self.entity:
            return
            
        # Handle scroll input
        keys = pygame.key.get_pressed()
        dt = self.entity.delta_time
        
        if keys[pygame.K_UP]:
            self.scroll_y = max(0, self.scroll_y - self.scroll_speed * dt)
        elif keys[pygame.K_DOWN]:
            self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed * dt)
            
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEWHEEL:
            # Mouse wheel scrolling
            self.scroll_y = max(0, min(self.max_scroll, self.scroll_y - event.y * 30))
            
    def get_scroll_offset(self) -> float:
        """Get current scroll offset."""
        return self.scroll_y