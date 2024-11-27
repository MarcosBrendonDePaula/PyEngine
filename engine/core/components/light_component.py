import pygame
import math
import numpy as np
from typing import List, Tuple
from ..component import Component

class LightComponent(Component):
    def __init__(self, color=(255, 255, 255), intensity=1.0, radius=200, num_rays=180):
        super().__init__()
        # Ensure color values are integers
        self.color = (
            min(255, max(0, int(color[0]))),
            min(255, max(0, int(color[1]))),
            min(255, max(0, int(color[2])))
        )
        self.intensity = min(1.0, max(0.0, float(intensity)))
        self.radius = int(radius)
        self.num_rays = num_rays
        
        # Create surface for light
        self.light_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        
        # Create the base light gradient once
        self._create_base_light()
        
        # Cache
        self.obstacles = []
        self._needs_update = True
        self._last_position = None
    
    def _create_base_light(self):
        """Create the base light gradient"""
        center = (self.radius, self.radius)
        
        # Clear surface
        self.light_surface.fill((0, 0, 0, 0))
        
        # Create gradient
        max_alpha = int(255 * self.intensity)
        for r in range(self.radius, 0, -1):
            alpha = int((r / self.radius) * max_alpha)
            alpha = max_alpha - alpha  # Invert alpha so center is brightest
            color = (*self.color, alpha)
            pygame.draw.circle(self.light_surface, color, center, r)
    
    def update_obstacles(self, obstacles: List[List[Tuple[float, float]]]):
        """Update the list of obstacles that cast shadows"""
        self.obstacles = obstacles
        self._needs_update = True
    
    def render(self, screen: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)):
        """Render the light"""
        if not self.enabled or not self.entity:
            return
        
        # Get light position
        light_pos = (
            int(self.entity.position.x - self.radius + camera_offset[0]),
            int(self.entity.position.y - self.radius + camera_offset[1])
        )
        
        # Draw light with additive blending
        screen.blit(self.light_surface, light_pos, special_flags=pygame.BLEND_RGBA_ADD)
