import pygame
from typing import Tuple, List, Optional, Set
from ..component import Component

class Collider(Component):
    def __init__(self, width: float, height: float, is_trigger: bool = False):
        super().__init__()
        self.width = width
        self.height = height
        self.is_trigger = is_trigger
        self.offset = pygame.math.Vector2(0, 0)
        self.colliding_entities: Set[int] = set()  # Set of colliding entity IDs
        self.collision_layer = 0
        self.collision_mask = 1  # By default, collide with layer 0

    def get_rect(self) -> pygame.Rect:
        """Get the collision rectangle in world space"""
        if not self.entity:
            return pygame.Rect(0, 0, self.width, self.height)
        
        return pygame.Rect(
            self.entity.position.x + self.offset.x - self.width/2,
            self.entity.position.y + self.offset.y - self.height/2,
            self.width,
            self.height
        )

    def check_collision(self, other: 'Collider') -> bool:
        """Check if this collider intersects with another"""
        # Check collision layers
        if not (self.collision_mask & (1 << other.collision_layer)):
            return False

        return self.get_rect().colliderect(other.get_rect())

    def on_collision_enter(self, other_entity: 'Entity'):
        """Called when collision starts"""
        self.colliding_entities.add(other_entity.id)

    def on_collision_exit(self, other_entity: 'Entity'):
        """Called when collision ends"""
        self.colliding_entities.discard(other_entity.id)

    def set_collision_layer(self, layer: int):
        """Set the collision layer (0-31)"""
        self.collision_layer = min(max(layer, 0), 31)

    def set_collision_mask(self, mask: int):
        """Set the collision mask (which layers to collide with)"""
        self.collision_mask = mask

    def set_size(self, width: float, height: float):
        """Set the collider size"""
        self.width = width
        self.height = height

    def set_offset(self, x: float, y: float):
        """Set the collider offset from entity position"""
        self.offset.x = x
        self.offset.y = y

    def is_colliding_with(self, entity_id: int) -> bool:
        """Check if currently colliding with a specific entity"""
        return entity_id in self.colliding_entities

    def render_debug(self, screen: pygame.Surface, camera_offset=(0, 0)):
        """Render collision bounds for debugging"""
        rect = self.get_rect()
        rect.x -= camera_offset[0]
        rect.y -= camera_offset[1]
        
        # Draw collision bounds in yellow for triggers, red for normal colliders
        color = (255, 255, 0) if self.is_trigger else (255, 0, 0)
        pygame.draw.rect(screen, color, rect, 1)
