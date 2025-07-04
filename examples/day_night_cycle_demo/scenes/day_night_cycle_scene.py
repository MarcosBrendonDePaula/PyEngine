import pygame
import math
import random
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.rectangle_renderer import RectangleRenderer

class DayNightCycleScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.time = 0
        self.day_length = 10  # seconds for a full day/night cycle
        self.background = None
        self.bg_renderer = None
        self.sun = None
        self.moon = None
        self.stars = []  # List of star positions
        
    def on_initialize(self):
        """Initialize scene objects and components"""
        # Create background
        self.background = Entity()
        self.bg_renderer = RectangleRenderer(
            width=800,
            height=600,
            color=(135, 206, 235)  # Sky blue
        )
        self.background.add_component(self.bg_renderer)
        self.background.position = pygame.math.Vector2(400, 300)  # Center of screen
        self.add_entity(self.background)
        
        # Create sun
        self.sun = Entity()
        self.sun_renderer = RectangleRenderer(
            width=60,
            height=60,
            color=(255, 255, 0)  # Yellow
        )
        self.sun.add_component(self.sun_renderer)
        self.add_entity(self.sun)
        
        # Create moon
        self.moon = Entity()
        self.moon_renderer = RectangleRenderer(
            width=50,
            height=50,
            color=(200, 200, 200)  # Light gray
        )
        self.moon.add_component(self.moon_renderer)
        self.add_entity(self.moon)
        
        # Generate random stars
        for _ in range(100):
            x = random.randint(0, 800)
            y = random.randint(0, 400)  # Only in upper portion of sky
            size = random.randint(1, 3)
            self.stars.append((x, y, size))
        
    def update(self, delta_time: float):
        """Update scene state"""
        super().update(delta_time)
        
        if not self._is_loaded:
            return
            
        # Update time using delta_time
        self.time += delta_time
        cycle_progress = (self.time % self.day_length) / self.day_length
        
        # Calculate celestial body positions
        # They move in a semicircle from left to right
        radius = 250  # Radius of the arc
        center_x = 400  # Center of the screen
        center_y = 550  # Below the bottom of the screen
        
        # Sun position (0 to π)
        sun_angle = cycle_progress * math.pi
        sun_x = center_x - radius * math.cos(sun_angle)
        sun_y = center_y - radius * math.sin(sun_angle)
        self.sun.position = pygame.math.Vector2(sun_x, sun_y)
        
        # Moon position (π to 2π)
        moon_angle = (cycle_progress + 0.5) % 1.0 * math.pi
        moon_x = center_x - radius * math.cos(moon_angle)
        moon_y = center_y - radius * math.sin(moon_angle)
        self.moon.position = pygame.math.Vector2(moon_x, moon_y)
        
        # Update sky color based on sun position
        if cycle_progress < 0.5:  # Day time
            # Transition from dawn to noon
            progress = cycle_progress * 2
            r = int(lerp(240, 135, progress))  # From light pink to sky blue
            g = int(lerp(210, 206, progress))
            b = int(lerp(210, 235, progress))
        else:  # Night time
            # Transition from noon to dusk to night
            progress = (cycle_progress - 0.5) * 2
            r = int(lerp(135, 20, progress))  # From sky blue to dark blue
            g = int(lerp(206, 24, progress))
            b = int(lerp(235, 82, progress))
        
        self.bg_renderer.set_color((r, g, b))
        
        # Update sun brightness based on height
        sun_brightness = min(255, max(0, int(255 * math.sin(sun_angle))))
        self.sun_renderer.set_color((255, 255, sun_brightness))
        
        # Update moon brightness based on height
        moon_brightness = min(255, max(0, int(255 * math.sin(moon_angle))))
        self.moon_renderer.set_color((moon_brightness, moon_brightness, moon_brightness))
    
    def render(self, screen: pygame.Surface):
        """Custom render to draw background, stars, sun, and moon"""
        # Draw background
        screen.fill(self.bg_renderer.color)
        
        # Draw stars (only visible during night)
        cycle_progress = (self.time % self.day_length) / self.day_length
        if cycle_progress >= 0.4 and cycle_progress <= 0.9:  # Show stars during dusk/night/dawn
            star_alpha = 0
            if cycle_progress < 0.5:  # Dawn
                star_alpha = int(255 * (1 - (cycle_progress - 0.4) * 10))
            elif cycle_progress > 0.8:  # Dusk
                star_alpha = int(255 * ((cycle_progress - 0.8) * 10))
            else:  # Night
                star_alpha = 255
                
            star_surface = pygame.Surface((800, 600), pygame.SRCALPHA)
            for x, y, size in self.stars:
                pygame.draw.circle(star_surface, (255, 255, 255, star_alpha), (x, y), size)
            screen.blit(star_surface, (0, 0))
        
        # Draw sun
        if self.sun and self.sun.position:
            # Draw sun glow
            glow_surface = pygame.Surface((800, 600), pygame.SRCALPHA)
            glow_radius = 40
            for r in range(glow_radius, 0, -2):
                alpha = int((r / glow_radius) * 100)
                pygame.draw.circle(
                    glow_surface,
                    (*self.sun_renderer.color[:2], alpha),
                    (int(self.sun.position.x), int(self.sun.position.y)),
                    r
                )
            screen.blit(glow_surface, (0, 0))
            
            # Draw sun
            pygame.draw.circle(
                screen,
                self.sun_renderer.color,
                (int(self.sun.position.x), int(self.sun.position.y)),
                30
            )
            
        # Draw moon
        if self.moon and self.moon.position:
            # Draw moon glow
            glow_surface = pygame.Surface((800, 600), pygame.SRCALPHA)
            glow_radius = 35
            for r in range(glow_radius, 0, -2):
                alpha = int((r / glow_radius) * 50)
                pygame.draw.circle(
                    glow_surface,
                    (*self.moon_renderer.color[:2], alpha),
                    (int(self.moon.position.x), int(self.moon.position.y)),
                    r
                )
            screen.blit(glow_surface, (0, 0))
            
            # Draw moon
            pygame.draw.circle(
                screen,
                self.moon_renderer.color,
                (int(self.moon.position.x), int(self.moon.position.y)),
                25
            )
    
    def load_resources(self):
        """Mark scene as loaded since we don't have external resources"""
        self._is_loaded = True
        self._loading_progress = 100

def lerp(start, end, progress):
    return start + (end - start) * progress
