import pygame
import math
import numpy as np
from typing import List, Tuple, Optional
from ..component import Component
from .collider import Collider, line_segments_intersect

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
        
        # Light properties
        self.light_length = 500
        self.light_width = 300
        
        # Raytracing properties
        self.ray_count = 32  # Number of rays to cast
        self.colliders: List[Collider] = []
    
    def _calculate_light_direction(self) -> pygame.math.Vector2:
        angle_rad = math.radians(self.angle)
        return pygame.math.Vector2(math.cos(angle_rad), math.sin(angle_rad))
    
    def _cast_ray(self, start: Tuple[float, float], direction: pygame.math.Vector2, 
                  max_distance: float) -> Optional[Tuple[float, float]]:
        """Cast a ray and return the closest intersection point"""
        end = (
            start[0] + direction.x * max_distance,
            start[1] + direction.y * max_distance
        )
        
        closest_point = end
        closest_distance = max_distance
        
        # Check intersection with all colliders
        for collider in self.colliders:
            if isinstance(collider, Collider):
                points = collider.get_rect_points()
                
                # Check each edge of the collider
                for i in range(len(points)):
                    p1 = points[i]
                    p2 = points[(i + 1) % len(points)]
                    
                    if line_segments_intersect(start, end, p1, p2):
                        # Calculate intersection point
                        x1, y1 = start
                        x2, y2 = end
                        x3, y3 = p1
                        x4, y4 = p2
                        
                        # Line-line intersection formula
                        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
                        if denominator == 0:
                            continue
                            
                        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
                        
                        if 0 <= t <= 1:
                            # Calculate intersection point
                            intersection_x = x1 + t * (x2 - x1)
                            intersection_y = y1 + t * (y2 - y1)
                            
                            # Check if this is the closest intersection
                            distance = math.sqrt(
                                (intersection_x - start[0])**2 + 
                                (intersection_y - start[1])**2
                            )
                            if distance < closest_distance:
                                closest_distance = distance
                                closest_point = (intersection_x, intersection_y)
        
        return closest_point
    
    def render(self, screen: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)):
        if not self.enabled or not self.entity:
            return
        
        # Get light position and direction
        light_pos = self.entity.position
        center = (int(light_pos.x), int(light_pos.y))
        light_dir = self._calculate_light_direction()
        
        # Create surface for light
        light_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        
        # Calculate cone angles
        cone_angle = math.radians(30)  # 30 degree cone
        base_angle = math.atan2(light_dir.y, light_dir.x)
        start_angle = base_angle - cone_angle
        end_angle = base_angle + cone_angle
        
        # Cast rays in a fan pattern
        ray_points = [center]  # Start from center point
        angle_step = (2 * cone_angle) / (self.ray_count - 1)
        
        for i in range(self.ray_count):
            angle = start_angle + angle_step * i
            ray_dir = pygame.math.Vector2(math.cos(angle), math.sin(angle))
            
            # Calculate end point based on light width at max distance
            distance = self.light_length
            spread = (i / (self.ray_count - 1) - 0.5) * 2  # -1 to 1
            target_width = self.light_width * abs(spread)
            
            end_point = self._cast_ray(center, ray_dir, distance)
            if end_point:
                ray_points.append(end_point)
        
        # Draw light with gradient
        for i in range(10):
            alpha = int(100 * (1 - i/10) * self.intensity)
            scale = 1 - i/20
            scaled_points = []
            
            # First point is always the center
            scaled_points.append(center)
            
            # Scale other points from center
            for point in ray_points[1:]:
                dx = point[0] - center[0]
                dy = point[1] - center[1]
                scaled_x = center[0] + dx * scale
                scaled_y = center[1] + dy * scale
                scaled_points.append((scaled_x, scaled_y))
            
            if len(scaled_points) > 2:  # Need at least 3 points for a polygon
                pygame.draw.polygon(light_surface, (*self.color, alpha), scaled_points)
        
        # Apply lighting
        screen.blit(light_surface, (0, 0))
        
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
    
    def update_colliders(self, colliders: List[Collider]):
        """Update the list of colliders that can block light"""
        self.colliders = colliders
    
    def set_angle(self, angle: float):
        self.angle = angle % 360
