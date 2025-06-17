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
        self.is_static = False

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

        # Determine which overlap is smaller to resolve along that axis
        if abs(overlap_x) < abs(overlap_y):
            # Horizontal collision
            if rect1.centerx < rect2.centerx:
                self.entity.position.x -= overlap_x
            else:
                self.entity.position.x += overlap_x
            self.velocity.x = -self.velocity.x * self.restitution
        else:
            # Vertical collision
            if rect1.centery < rect2.centery:
                self.entity.position.y -= overlap_y
                if self.velocity.y > 0:  # Only set grounded if moving downward
                    self.is_grounded = True
            else:
                self.entity.position.y += overlap_y
            self.velocity.y = -self.velocity.y * self.restitution

    def tick(self):
        if not self.enabled or not self.entity or self.is_static:
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

    def set_static(self, is_static: bool):
        """
        Marks the body as static (non-movable but collidable).
        """
        self.is_static = is_static
        self.is_kinematic = False  # Static bodies are not kinematic
        if is_static:
            self.velocity = pygame.math.Vector2(0, 0)
            self.forces = pygame.math.Vector2(0, 0)