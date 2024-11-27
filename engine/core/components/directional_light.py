import pygame
import math
import numpy as np
from typing import List, Tuple
from ..component import Component

class DirectionalLight(Component):
    def __init__(self, color=(255, 255, 255), intensity=1.0, angle=45):
        super().__init__()
        self.color = (
            min(255, max(0, int(color[0]))),
            min(255, max(0, int(color[1]))),
            min(255, max(0, int(color[2])))
        )
        self.intensity = min(2.0, max(0.0, float(intensity)))
        self.angle = angle
        self.obstacles = []
        
        # Light properties
        self.light_length = 500
        self.light_width = 300
    
    def _calculate_light_direction(self) -> pygame.math.Vector2:
        angle_rad = math.radians(self.angle)
        return pygame.math.Vector2(math.cos(angle_rad), math.sin(angle_rad))
    
    def _is_point_in_light_cone(self, point: Tuple[float, float], center: Tuple[float, float], 
                               light_dir: pygame.math.Vector2, perp: pygame.math.Vector2) -> bool:
        """Check if a point is within the light cone"""
        # Vector from center to point
        to_point = pygame.math.Vector2(point[0] - center[0], point[1] - center[1])
        
        # Check distance in light direction
        forward_dist = to_point.dot(light_dir)
        if forward_dist < 0 or forward_dist > self.light_length:
            return False
        
        # Check distance perpendicular to light direction
        side_dist = abs(to_point.dot(perp))
        # Calculate max allowed width at this distance
        max_width = (forward_dist / self.light_length) * (self.light_width / 2)
        
        return side_dist <= max_width
    
    def render(self, screen: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)):
        if not self.enabled or not self.entity:
            return
        
        # Get light position and direction
        light_pos = self.entity.position
        center = (int(light_pos.x), int(light_pos.y))
        light_dir = self._calculate_light_direction()
        perp = pygame.math.Vector2(-light_dir.y, light_dir.x)
        
        # Calculate light cone points
        half_width = self.light_width / 2
        start_width = half_width * 0.2
        
        # Light cone vertices
        light_points = [
            # Start points (narrow)
            (center[0] + perp.x * start_width, center[1] + perp.y * start_width),
            (center[0] - perp.x * start_width, center[1] - perp.y * start_width),
            # End points (wide)
            (center[0] + light_dir.x * self.light_length - perp.x * half_width,
             center[1] + light_dir.y * self.light_length - perp.y * half_width),
            (center[0] + light_dir.x * self.light_length + perp.x * half_width,
             center[1] + light_dir.y * self.light_length + perp.y * half_width)
        ]
        
        # Create surfaces for light and shadows
        light_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        shadow_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        
        # Draw light cone
        pygame.draw.polygon(light_surface, (*self.color, 100), light_points)
        
        # Draw shadows only for obstacles in light cone
        for obstacle in self.obstacles:
            # Get points in light cone
            visible_points = []
            shadow_points = []
            
            for i, point in enumerate(obstacle):
                if self._is_point_in_light_cone(point, center, light_dir, perp):
                    visible_points.append(point)
                    # Add original point and its shadow
                    shadow_points.append(point)
                    shadow_point = (
                        point[0] + light_dir.x * (self.light_length - math.sqrt((point[0] - center[0])**2 + (point[1] - center[1])**2)),
                        point[1] + light_dir.y * (self.light_length - math.sqrt((point[0] - center[0])**2 + (point[1] - center[1])**2))
                    )
                    shadow_points.append(shadow_point)
            
            # Draw visible part of obstacle if we have enough points
            if len(visible_points) >= 3:
                pygame.draw.polygon(shadow_surface, (0, 0, 0, 255), visible_points)
            
            # Draw shadow if we have enough points
            if len(shadow_points) >= 4:
                # Draw shadow polygons between each pair of points
                for i in range(0, len(shadow_points) - 2, 2):
                    quad = [
                        shadow_points[i],
                        shadow_points[i + 1],
                        shadow_points[i + 3],
                        shadow_points[i + 2]
                    ]
                    pygame.draw.polygon(shadow_surface, (0, 0, 0, 200), quad)
        
        # Apply lighting and shadows
        screen.blit(light_surface, (0, 0))
        screen.blit(shadow_surface, (0, 0))
        
        # Draw light center indicator
        pygame.draw.circle(screen, (0, 0, 0), center, 8)
        pygame.draw.circle(screen, self.color, center, 6)
        
        # Draw direction indicator
        end_point = (
            center[0] + light_dir.x * 20,
            center[1] + light_dir.y * 20
        )
        pygame.draw.line(screen, (0, 0, 0), center, end_point, 4)
        pygame.draw.line(screen, self.color, center, end_point, 2)
    
    def update_obstacles(self, obstacles: List[List[Tuple[float, float]]]):
        self.obstacles = obstacles
    
    def set_angle(self, angle: float):
        self.angle = angle % 360
