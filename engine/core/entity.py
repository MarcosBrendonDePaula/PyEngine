import pygame
from typing import Dict, Type, Optional
from .component import Component

class Entity:
    def __init__(self, x: float = 0, y: float = 0):
        self.id = id(self)
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)
        self.rotation = 0
        self.scale = pygame.math.Vector2(1, 1)
        self.active = True
        self.visible = True
        self.scene = None
        
        # Component system
        self.components: Dict[Type[Component], Component] = {}

    def add_component(self, component: Component) -> Component:
        """Add a component to the entity"""
        component_type = type(component)
        if component_type in self.components:
            raise ValueError(f"Component of type {component_type.__name__} already exists")
        
        self.components[component_type] = component
        component.attach(self)
        return component

    def get_component(self, component_type: Type[Component]) -> Optional[Component]:
        """Get a component by its type"""
        return self.components.get(component_type)

    def remove_component(self, component_type: Type[Component]) -> None:
        """Remove a component by its type"""
        if component_type in self.components:
            self.components[component_type].detach()
            del self.components[component_type]

    def has_component(self, component_type: Type[Component]) -> bool:
        """Check if entity has a component of the specified type"""
        return component_type in self.components

    def set_position(self, x: float, y: float):
        self.position.x = x
        self.position.y = y

    def set_velocity(self, x: float, y: float):
        self.velocity.x = x
        self.velocity.y = y

    def set_acceleration(self, x: float, y: float):
        self.acceleration.x = x
        self.acceleration.y = y

    def move(self, dx: float, dy: float):
        self.position.x += dx
        self.position.y += dy

    def tick(self):
        """Update method to be called each frame for game logic"""
        if not self.active:
            return

        # Update velocity based on acceleration
        self.velocity += self.acceleration

        # Update position based on velocity
        self.position += self.velocity

        # Update all components
        for component in self.components.values():
            if component.enabled:
                component.tick()

    def render(self, screen: pygame.Surface, camera_offset=(0, 0)):
        """Render method to be called each frame for drawing"""
        if not self.visible:
            return

        # Render all components
        for component in self.components.values():
            if component.enabled:
                component.render(screen, camera_offset)

    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events"""
        # Pass events to all components
        for component in self.components.values():
            if component.enabled:
                component.handle_event(event)
