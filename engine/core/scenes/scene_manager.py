from typing import Dict, Optional, List
import pygame
from examples.scenes.loading_scene import LoadingScene

class SceneManager:
    def __init__(self):
        print("Initializing SceneManager")
        self._scenes: Dict[str, object] = {}
        self._current_scene = None
        self._scene_stack: List[object] = []  # For scene stacking
        self._interface = None
        self._is_transitioning = False
        self._transition_alpha = 0
        self._transition_surface = None
        self._next_scene_name = None
        self._persistent_data = {}  # For storing persistent data between scenes
        self._loading_scene = None
        print("SceneManager initialized")

    def set_interface(self, interface):
        """Set the interface reference"""
        print("Setting interface reference in SceneManager")
        self._interface = interface
        # Initialize loading scene
        self._loading_scene = LoadingScene()
        self._loading_scene.set_interface(interface)
        self._loading_scene.initialize()

    def add_scene(self, name: str, scene) -> None:
        """Add a scene to the manager"""
        print(f"Adding scene to manager: {name}")
        if name in self._scenes:
            print(f"Scene {name} already exists, skipping add")
            return
            
        self._scenes[name] = scene
        if hasattr(scene, 'set_interface'):
            print(f"Setting interface for scene: {name}")
            scene.set_interface(self._interface)
        # Initialize scene if it has the method
        if hasattr(scene, 'initialize') and not getattr(scene, '_is_initialized', False):
            print(f"Initializing scene: {name}")
            scene.initialize()
            scene._is_initialized = True
        print(f"Scene added: {name}")

    def set_scene(self, name: str, transition: bool = True) -> None:
        """Set the current scene with optional transition effect"""
        print(f"Setting current scene to: {name}")
        if name not in self._scenes:
            raise ValueError(f"Scene '{name}' not found")
            
        # If we're already on this scene or already transitioning, don't change
        if self._current_scene == self._scenes[name] or self._is_transitioning:
            print(f"Already on scene {name} or transitioning, skipping change")
            return

        # Reset loading state of target scene
        target_scene = self._scenes[name]
        if hasattr(target_scene, '_is_loaded'):
            target_scene._is_loaded = False
        if hasattr(target_scene, '_loading_progress'):
            target_scene._loading_progress = 0
        if hasattr(target_scene, '_current_step'):
            target_scene._current_step = 0

        if transition:
            print(f"Starting transition to {name} through loading scene")
            self._loading_scene.set_target_scene(name)
            self._change_scene('loading')
        else:
            self._change_scene(name)

    def _change_scene(self, name: str) -> None:
        """Actually change the scene"""
        print(f"Changing scene to: {name}")
        # Call onExit for current scene
        if self._current_scene and hasattr(self._current_scene, 'on_exit'):
            print("Calling on_exit for current scene")
            self._current_scene.on_exit()

        old_scene = self._current_scene
        
        # Handle loading scene specially
        if name == 'loading':
            print("Switching to loading scene")
            self._current_scene = self._loading_scene
        else:
            print(f"Switching to scene: {name}")
            self._current_scene = self._scenes[name]

        # Call onEnter for new scene
        if hasattr(self._current_scene, 'on_enter'):
            print("Calling on_enter for new scene")
            self._current_scene.on_enter(old_scene)
        print(f"Scene changed to: {name}")

    def get_current_scene(self) -> Optional[object]:
        """Get the current scene"""
        return self._current_scene

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle events in the current scene"""
        if self._current_scene and hasattr(self._current_scene, 'handle_event'):
            self._current_scene.handle_event(event)

    def update(self) -> None:
        """Update the current scene"""
        if self._current_scene and hasattr(self._current_scene, 'update'):
            self._current_scene.update()

    def render(self, screen: pygame.Surface) -> None:
        """Render the current scene"""
        if self._current_scene and hasattr(self._current_scene, 'render'):
            self._current_scene.render(screen)

    def store_persistent_data(self, key: str, value: any) -> None:
        """Store data that persists between scenes"""
        print(f"Storing persistent data: {key} = {value}")
        self._persistent_data[key] = value

    def get_persistent_data(self, key: str, default: any = None) -> any:
        """Get persistent data by key"""
        return self._persistent_data.get(key, default)

    def clear_persistent_data(self) -> None:
        """Clear all persistent data"""
        self._persistent_data.clear()

    def cleanup(self) -> None:
        """Clean up all scenes"""
        print("Cleaning up all scenes")
        for name, scene in self._scenes.items():
            if hasattr(scene, 'cleanup'):
                scene.cleanup()
        if self._loading_scene and hasattr(self._loading_scene, 'cleanup'):
            self._loading_scene.cleanup()
        self._scenes.clear()
        self._current_scene = None
        self._scene_stack.clear()
        self._persistent_data.clear()
        self._loading_scene = None
