import pygame
from typing import Optional, Tuple
from ..component import Component
from .collider import Collider

class Physics(Component):
    def __init__(self, mass: float = 1.0, gravity: float = 0.0, friction: float = 0.1):
        super().__init__()
        self.mass = mass
        self.gravity = gravity
        self.friction = friction
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)
        self.forces = pygame.math.Vector2(0, 0)
        self.terminal_velocity = 1000.0  # Maximum velocity
        self.is_kinematic = False  # If True, ignores forces and gravity
        self.is_grounded = False
        self._collider: Optional[Collider] = None
        self.restitution = 0.5  # Bounce factor for collisions

    def attach(self, entity):
        """Called when component is attached to entity"""
        super().attach(entity)
        # Get reference to entity's collider if it exists
        self._collider = self.entity.get_component(Collider)

    def apply_force(self, force_x: float, force_y: float):
        """Apply a force to the entity"""
        if self.is_kinematic:
            return
        self.forces.x += force_x
        self.forces.y += force_y

    def apply_impulse(self, impulse_x: float, impulse_y: float):
        """Apply an instantaneous force (directly changes velocity)"""
        if self.is_kinematic:
            return
        self.velocity.x += impulse_x / self.mass
        self.velocity.y += impulse_y / self.mass

    def set_velocity(self, velocity_x: float, velocity_y: float):
        """Directly set the velocity"""
        self.velocity.x = velocity_x
        self.velocity.y = velocity_y

    def resolve_collision(self, other_collider: Collider):
        """Resolve collision with another collider"""
        if not self._collider or self.is_kinematic:
            return

        # Get the rectangles for both colliders
        rect1 = self._collider.get_rect()
        rect2 = other_collider.get_rect()

        # Calculate overlap
        overlap_x = min(rect1.right, rect2.right) - max(rect1.left, rect2.left)
        overlap_y = min(rect1.bottom, rect2.bottom) - max(rect1.top, rect2.top)

        # Get the centers of both rectangles
        center1 = pygame.math.Vector2(rect1.centerx, rect1.centery)
        center2 = pygame.math.Vector2(rect2.centerx, rect2.centery)

        # Calculate direction from center1 to center2
        direction = center2 - center1
        if direction.length() > 0:
            direction.normalize_ip()

        # Determine the separation distance needed
        separation = max(overlap_x, overlap_y) * 1.1  # Add 10% extra separation

        # Move this entity away from the collision
        self.entity.position.x -= direction.x * separation
        self.entity.position.y -= direction.y * separation

        # Calculate reflection vector for velocity
        if abs(overlap_x) < abs(overlap_y):
            # Horizontal collision
            self.velocity.x = -self.velocity.x * self.restitution
            # Apply additional horizontal separation force
            self.apply_impulse(-direction.x * 10.0, 0)
        else:
            # Vertical collision
            self.velocity.y = -self.velocity.y * self.restitution
            # Apply additional vertical separation force
            self.apply_impulse(0, -direction.y * 10.0)

    def tick(self):
        if not self.enabled or not self.entity:
            return

        if not self.is_kinematic:
            # Apply gravity
            self.forces.y += self.mass * self.gravity

            # Calculate acceleration from forces
            self.acceleration.x = self.forces.x / self.mass
            self.acceleration.y = self.forces.y / self.mass

            # Update velocity
            self.velocity.x += self.acceleration.x
            self.velocity.y += self.acceleration.y

            # Apply friction
            if self.is_grounded:
                self.velocity.x *= (1 - self.friction)

            # Limit to terminal velocity
            velocity_magnitude = self.velocity.length()
            if velocity_magnitude > self.terminal_velocity:
                self.velocity.scale_to_length(self.terminal_velocity)

            # Store previous position for collision resolution
            prev_pos = pygame.math.Vector2(self.entity.position)

            # Update position
            self.entity.position.x += self.velocity.x
            self.entity.position.y += self.velocity.y

            # Reset grounded state (will be set true if collision detected below)
            self.is_grounded = False

        # Reset forces for next frame
        self.forces.x = 0
        self.forces.y = 0

    def set_kinematic(self, kinematic: bool):
        """Set whether the physics component is kinematic"""
        self.is_kinematic = kinematic
        if kinematic:
            self.velocity.x = 0
            self.velocity.y = 0
            self.forces.x = 0
            self.forces.y = 0

    def set_mass(self, mass: float):
        """Set the mass of the physics component"""
        if mass <= 0:
            raise ValueError("Mass must be greater than 0")
        self.mass = mass

    def set_gravity(self, gravity: float):
        """Set the gravity scale for this physics component"""
        self.gravity = gravity

    def set_friction(self, friction: float):
        """Set the friction coefficient"""
        self.friction = max(0.0, min(1.0, friction))
