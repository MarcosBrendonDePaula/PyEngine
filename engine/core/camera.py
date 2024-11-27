import pygame
from typing import Tuple, Optional
from .entity import Entity

class Camera:
    def __init__(self, width: int, height: int):
        self.position = pygame.math.Vector2(0, 0)
        self.width = width
        self.height = height
        self.zoom = 1.0
        self.target: Optional[Entity] = None
        self.bounds = None  # (x, y, width, height)
        self.lerp_speed = 0.1  # Camera smoothing factor

    def set_bounds(self, x: int, y: int, width: int, height: int):
        """Set the camera bounds to prevent showing empty space"""
        self.bounds = (x, y, width, height)

    def set_target(self, target: Entity):
        """Set an entity for the camera to follow"""
        self.target = target

    def follow_target(self):
        """Update camera position to follow target with smooth movement"""
        if not self.target:
            return

        target_x = self.target.position.x - self.width / 2
        target_y = self.target.position.y - self.height / 2

        # Smooth camera movement using linear interpolation
        self.position.x += (target_x - self.position.x) * self.lerp_speed
        self.position.y += (target_y - self.position.y) * self.lerp_speed

        # Apply bounds if set
        if self.bounds:
            self.position.x = max(self.bounds[0], min(self.position.x, 
                                self.bounds[0] + self.bounds[2] - self.width))
            self.position.y = max(self.bounds[1], min(self.position.y, 
                                self.bounds[1] + self.bounds[3] - self.height))

    def world_to_screen(self, world_pos: Tuple[float, float]) -> Tuple[float, float]:
        """Convert world coordinates to screen coordinates"""
        screen_x = (world_pos[0] - self.position.x) * self.zoom
        screen_y = (world_pos[1] - self.position.y) * self.zoom
        return (screen_x, screen_y)

    def screen_to_world(self, screen_pos: Tuple[float, float]) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates"""
        world_x = screen_pos[0] / self.zoom + self.position.x
        world_y = screen_pos[1] / self.zoom + self.position.y
        return (world_x, world_y)

    def update(self):
        """Update camera position and zoom"""
        self.follow_target()

    def apply(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply camera transformations to a surface"""
        if self.zoom != 1.0:
            new_size = (int(surface.get_width() * self.zoom), 
                       int(surface.get_height() * self.zoom))
            return pygame.transform.scale(surface, new_size)
        return surface
