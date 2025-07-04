import pygame
import threading
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
        self.delta_time: float = 0.0  # Direct access to delta_time
        
        # Component system with thread safety
        self.components: Dict[Type[Component], Component] = {}
        self._component_lock = threading.RLock()  # Reentrant lock for nested component operations
        
        # Thread safety flags
        self._thread_safe_update = True  # Enable thread-safe update by default
        self._update_lock = threading.RLock() if self._thread_safe_update else None

    def add_component(self, component: T) -> T:
        """
        Add a component to the entity (thread-safe)
        
        Args:
            component (T): The component to add
            
        Returns:
            T: The added component of the specific type
            
        Raises:
            ValueError: If a component of the same type already exists
        """
        component_type: Type[Component] = type(component)
        
        with self._component_lock:
            if component_type in self.components:
                raise ValueError(f"Component of type {component_type.__name__} already exists")
            
            self.components[component_type] = component
            component.attach(self)
            return component

    def get_component(self, component_type: Type[T]) -> Optional[T]:
        """
        Get a component by its type (thread-safe)
        
        Args:
            component_type (Type[T]): The type of component to get
            
        Returns:
            Optional[T]: The component if found, None otherwise
        """
        with self._component_lock:
            return self.components.get(component_type)

    def remove_component(self, component_type: Type[Component]) -> None:
        """
        Remove a component by its type (thread-safe)
        
        Args:
            component_type (Type[Component]): The type of component to remove
        """
        with self._component_lock:
            if component_type in self.components:
                self.components[component_type].detach()
                del self.components[component_type]

    def has_component(self, component_type: Type[Component]) -> bool:
        """
        Check if entity has a component of the specified type (thread-safe)
        
        Args:
            component_type (Type[Component]): The type of component to check for
            
        Returns:
            bool: True if the component exists, False otherwise
        """
        with self._component_lock:
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

    def update(self) -> None:
        """Update method to be called each frame for game logic (thread-safe)"""
        if not self.active:
            return

        # Use lock only if thread safety is enabled
        if self._thread_safe_update and self._update_lock:
            with self._update_lock:
                self._perform_update()
        else:
            self._perform_update()
            
    def _perform_update(self) -> None:
        """Internal update method without locking."""
        # Update velocity based on acceleration
        self.velocity += self.acceleration * self.delta_time

        # Update position based on velocity
        self.position += self.velocity * self.delta_time

        # Update all components (with component lock)
        with self._component_lock:
            # Create a copy of values to avoid modification during iteration
            components = list(self.components.values())
            
        # Update components outside the lock to avoid nested locking issues
        for component in components:
            if component.enabled:
                try:
                    component.update()
                except Exception as e:
                    print(f"Error updating component {type(component).__name__} on entity {self.id}: {e}")
                    
    def set_thread_safe_update(self, enabled: bool) -> None:
        """Enable or disable thread-safe updates for this entity."""
        self._thread_safe_update = enabled
        if enabled and self._update_lock is None:
            self._update_lock = threading.RLock()
        elif not enabled:
            self._update_lock = None

    def render(self, screen: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)) -> None:
        """
        Render method to be called each frame for drawing (thread-safe)
        
        Args:
            screen (pygame.Surface): The surface to render to
            camera_offset (Tuple[float, float]): The camera offset to apply
        """
        if not self.visible:
            return

        # Get components safely
        with self._component_lock:
            components = list(self.components.values())
            
        # Render components outside the lock
        for component in components:
            if component.enabled:
                try:
                    component.render(screen, camera_offset)
                except Exception as e:
                    print(f"Error rendering component {type(component).__name__} on entity {self.id}: {e}")

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events (thread-safe)
        
        Args:
            event (pygame.event.Event): The event to handle
        """
        # Get components safely
        with self._component_lock:
            components = list(self.components.values())
            
        # Handle events outside the lock
        for component in components:
            if component.enabled:
                try:
                    component.handle_event(event)
                except Exception as e:
                    print(f"Error handling event in component {type(component).__name__} on entity {self.id}: {e}")
