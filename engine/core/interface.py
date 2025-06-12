import pygame
from typing import Tuple, Optional, Union
from .scenes.scene_manager import SceneManager

class Interface:
    def __init__(self, 
                 screen_or_title: Union[pygame.Surface, str],
                 size: Optional[Tuple[int, int]] = None):
        print("Initializing Interface")
        pygame.init()
        pygame.font.init()  # Initialize font system
        
        # Handle parameters based on type
        if isinstance(screen_or_title, pygame.Surface):
            # Use existing screen
            self.screen = screen_or_title
            self.size = self.screen.get_size()
            self.title = "PyEngine Game"
        else:
            # Create new screen with title
            self.title = screen_or_title
            self.size = size or (800, 600)
            self.screen = pygame.display.set_mode(self.size)
            pygame.display.set_caption(self.title)
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.fps = 60
        self.scene_manager = SceneManager()
        self.scene_manager.set_interface(self)  # Set interface reference in scene manager
        print("Interface initialized")

    def set_scene(self, name: str, scene):
        """Add and set a scene as current"""
        print(f"Setting scene: {name}")
        # Set interface reference before adding scene
        scene.set_interface(self)
        # Initialize scene before adding it
        if hasattr(scene, 'initialize'):
            print(f"Initializing scene: {name}")
            scene.initialize()
        # Only add the scene if it's not already added
        if name not in self.scene_manager._scenes:
            self.scene_manager.add_scene(name, scene)
        self.scene_manager.set_scene(name, transition=False)  # Disable transition to prevent loops
        print(f"Scene {name} set as current")

    def add_scene(self, name: str, scene):
        """Add a scene to the manager without setting it as current"""
        print(f"Adding scene: {name}")
        # Set interface reference before adding scene
        scene.set_interface(self)
        # Initialize scene before adding it
        if hasattr(scene, 'initialize'):
            print(f"Initializing scene: {name}")
            scene.initialize()
        self.scene_manager.add_scene(name, scene)
        print(f"Scene {name} added")

    def change_scene(self, name: str):
        """Change to a different scene"""
        print(f"Changing to scene: {name}")
        self.scene_manager.set_scene(name)

    def get_current_scene(self):
        """Get the current active scene"""
        return self.scene_manager.get_current_scene()

    def handle_events(self):
        """Process all events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                self.scene_manager.handle_event(event)

    def update(self):
        """Update the current scene"""
        self.scene_manager.update()

    def render(self):
        """Render the current scene"""
        self.screen.fill((0, 0, 0))  # Clear screen with black
        current_scene = self.scene_manager.get_current_scene()
        self.scene_manager.render(self.screen)
        pygame.display.flip()

    def run(self):
        """Main game loop"""
        print("Starting game loop")
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            delta_time = self.clock.tick(self.fps) / 1000.0  # Convert milliseconds to seconds
            self.scene_manager.update(delta_time)

        # Cleanup
        print("Cleaning up")
        self.scene_manager.cleanup()
        pygame.quit()

    def set_fps(self, fps: int):
        """Set the target frame rate"""
        self.fps = max(1, fps)

    def get_fps(self) -> float:
        """Get the current frame rate"""
        return self.clock.get_fps()

    @property
    def width(self) -> int:
        """Get screen width"""
        return self.size[0]
    
    @property
    def height(self) -> int:
        """Get screen height"""
        return self.size[1]
