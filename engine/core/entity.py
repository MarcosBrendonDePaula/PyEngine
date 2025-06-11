import pygame
from typing import Dict, Type, Optional, Any, Tuple, TypeVar

from engine.core.component import Component

T = TypeVar('T', bound='Component')  # Type variable for components

class Entity:
    def __init__(self, x: float = 0, y: float = 0):
        self.id: int = id(self)
        self.position: pygame.math.Vector2 = pygame.math.Vector2(x, y)
        self.velocity: pygame.math.Vector2 = pygame.math.Vector2(0, 0)
        self.acceleration: pygame.math.Vector2 = pygame.math.Vector2(0, 0)
        self.rotation: float = 0
        self.scale: pygame.math.Vector2 = pygame.math.Vector2(1, 1)
        self.active: bool = True
        self.visible: bool = True
        self.scene: Optional['BaseScene'] = None  # Forward reference for type hint
        
        # Component system
        self.components: Dict[Type[Component], Component] = {}

    def add_component(self, component: T) -> T:
        """
        Add a component to the entity
        
        Args:
            component (T): The component to add
            
        Returns:
            T: The added component of the specific type
            
        Raises:
            ValueError: If a component of the same type already exists
        """
        component_type: Type[Component] = type(component)
        if component_type in self.components:
            raise ValueError(f"Component of type {component_type.__name__} already exists")
        
        self.components[component_type] = component
        component.attach(self)
        return component

    def get_component(self, component_type: Type[T]) -> Optional[T]:
        """
        Get a component by its type
        
        Args:
            component_type (Type[T]): The type of component to get
            
        Returns:
            Optional[T]: The component if found, None otherwise
        """
        return self.components.get(component_type)

    def remove_component(self, component_type: Type[Component]) -> None:
        """
        Remove a component by its type
        
        Args:
            component_type (Type[Component]): The type of component to remove
        """
        if component_type in self.components:
            self.components[component_type].detach()
            del self.components[component_type]

    def has_component(self, component_type: Type[Component]) -> bool:
        """
        Check if entity has a component of the specified type
        
        Args:
            component_type (Type[Component]): The type of component to check for
            
        Returns:
            bool: True if the component exists, False otherwise
        """
        return component_type in self.components

    def set_position(self, x: float, y: float) -> None:
        """
        Set the entity's position
        
        Args:
            x (float): X coordinate
            y (float): Y coordinate
        """
        self.position.x = x
        self.position.y = y

    def set_velocity(self, x: float, y: float) -> None:
        """
        Set the entity's velocity
        
        Args:
            x (float): X velocity
            y (float): Y velocity
        """
        self.velocity.x = x
        self.velocity.y = y

    def set_acceleration(self, x: float, y: float) -> None:
        """
        Set the entity's acceleration
        
        Args:
            x (float): X acceleration
            y (float): Y acceleration
        """
        self.acceleration.x = x
        self.acceleration.y = y

    def move(self, dx: float, dy: float) -> None:
        """
        Move the entity by a delta amount
        
        Args:
            dx (float): Change in X position
            dy (float): Change in Y position
        """
        self.position.x += dx
        self.position.y += dy

    def tick(self) -> None:
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

    def render(self, screen: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)) -> List[pygame.Rect]:
        """
        Render method to be called each frame for drawing
        
        Args:
            screen (pygame.Surface): The surface to render to
            camera_offset (Tuple[float, float]): The camera offset to apply
        """
        if not self.visible:
            return []

        rendered_rects = []
        # Render all components
        for component in self.components.values():
            if component.enabled:
                rect = component.render(screen, camera_offset)
                if rect:
                    rendered_rects.append(rect)
        return rendered_rects

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events
        
        Args:
            event (pygame.event.Event): The event to handle
        """
        # Pass events to all components
        for component in self.components.values():
            if component.enabled:
                component.handle_event(event)
