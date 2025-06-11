import pygame
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional, Any
from ..camera import Camera
from ..resource_loader import ResourceLoader
from .collision_system import CollisionSystem

class BaseScene:
    def __init__(self, num_threads: int = None):
        self.num_threads = num_threads if num_threads is not None else mp.cpu_count()
        self.entities = []
        self.entity_groups: Dict[str, List] = {}
        self.interface = None
        self._resources = {}  # For storing resource IDs
        self._is_initialized = False
        self._is_loaded = False
        self._loading_progress = 0
        self.camera = None  # Will be initialized when interface is set
        self.resource_loader = ResourceLoader()  # Get the singleton instance
        self.collision_system = CollisionSystem()  # Initialize collision system
        
    def initialize(self):
        """Initialize scene resources. Called once when scene is added to manager."""
        if not self._is_initialized:
            self._is_initialized = True
            self.on_initialize()

    def on_initialize(self):
        """Override this method to perform one-time initialization"""
        pass

    def on_enter(self, previous_scene):
        """Called when scene becomes active"""
        pass

    def on_exit(self):
        """Called when switching to another scene"""
        pass

    def on_pause(self):
        """Called when another scene is pushed on top"""
        pass

    def on_resume(self):
        """Called when scene is resumed (top scene was popped)"""
        pass

    def set_num_threads(self, num_threads: int) -> None:
        """Update the number of threads used for parallel processing"""
        self.num_threads = max(1, num_threads)

    def set_interface(self, interface):
        """Set the interface reference and initialize camera"""
        self.interface = interface
        if interface:
            self.camera = Camera(interface.size[0], interface.size[1])

    def add_entity(self, entity, group: str = "default"):
        """Add an entity to the scene and group"""
        if entity not in self.entities:  # Prevent duplicate entities
            self.entities.append(entity)
            if group not in self.entity_groups:
                self.entity_groups[group] = []
            if entity not in self.entity_groups[group]:
                self.entity_groups[group].append(entity)
            # Set scene reference in entity
            entity.scene = self

    def remove_entity(self, entity, group: str = "default"):
        """Remove an entity from the scene and group"""
        if entity in self.entities:
            self.entities.remove(entity)
        if group in self.entity_groups and entity in self.entity_groups[group]:
            self.entity_groups[group].remove(entity)
        # Remove scene reference
        entity.scene = None

    def get_entities_by_group(self, group: str) -> List:
        """Get all entities in a specific group"""
        return self.entity_groups.get(group, [])

    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events"""
        if not self._is_loaded:
            return
            
        for entity in self.entities:
            if entity.active:
                entity.handle_event(event)

    def update(self):
        """Update all entities in the scene"""
        if not self._is_loaded:
            # If resources aren't loaded, update loading progress
            if not self._resources:
                self.load_resources()
            return

        # Update camera first
        if self.camera:
            self.camera.update()

        # Update all active entities in parallel
        active_entities = [e for e in self.entities if e.active]
        if active_entities:
            with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                futures = [executor.submit(entity.tick) for entity in active_entities]
                for future in futures:
                    future.result()

        # Update collision system
        self.collision_system.update(self.entities)

    def render(self, screen: pygame.Surface):
        """Render the scene"""
        if not self._is_loaded:
            self._render_loading_screen(screen)
            return

        # Fill background with black
        screen.fill((20, 20, 20))

        # Get camera offset
        camera_offset = (0, 0)
        if self.camera:
            camera_offset = (-self.camera.position.x, -self.camera.position.y)

        # First render non-UI entities with camera offset
        for entity in self.entities:
            if entity.visible and entity not in self.get_entities_by_group("ui"):
                entity.render(screen, camera_offset)

        # Then render UI entities without camera offset (in screen space)
        for entity in self.get_entities_by_group("ui"):
            if entity.visible:
                entity.render(screen, (0, 0))

    def _render_loading_screen(self, screen: pygame.Surface):
        """Render a simple loading screen"""
        screen.fill((20, 20, 20))
        if pygame.font.get_init():
            font = pygame.font.Font(None, 36)
            text = font.render(f"Loading... {self._loading_progress}%", True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(text, text_rect)

    def load_resources(self):
        """Override this to load scene-specific resources"""
        self._is_loaded = True
        self._loading_progress = 100

    def get_resource(self, name: str) -> Any:
        """Get a loaded resource by name"""
        if name in self._resources:
            return self.resource_loader.get_resource(self._resources[name])
        return None

    def add_resource(self, name: str, path: str) -> None:
        """Add a resource to the scene using the resource loader"""
        resource = self.resource_loader.load_resource(path, name)
        if resource:
            self._resources[name] = name

    def remove_resource(self, name: str) -> None:
        """Remove a resource from the scene"""
        if name in self._resources:
            self.resource_loader.unload_resource(self._resources[name])
            del self._resources[name]

    def cleanup(self):
        """Clean up scene resources"""
        # Clear entities
        for entity in self.entities[:]:  # Create a copy of the list to avoid modification during iteration
            self.remove_entity(entity)
        self.entity_groups.clear()
        
        # Clear resources
        for name in list(self._resources.keys()):
            self.remove_resource(name)
        self._resources.clear()
        self._is_loaded = False
        self._loading_progress = 0
        self.collision_system.clear()  # Clear collision system
