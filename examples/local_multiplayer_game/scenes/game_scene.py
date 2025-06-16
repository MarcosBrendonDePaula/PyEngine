import pygame
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.keyboard_controller import KeyboardController
from engine.core.components.rectangle_renderer import RectangleRenderer
from engine.core.components.collider import Collider
from engine.core.components.physics import Physics
from engine.core.components.debug_info import DebugInfoComponent
from engine.core.components.ui_component import UIComponent
from engine.core.scenes.collision_system import CollisionSystem
import os

class GameScene(BaseScene):
    def __init__(self, num_threads: int = None):
        super().__init__(num_threads)
        self.collision_system = CollisionSystem()
        self.paused = False
        self._is_loaded = False  # Start as not loaded
        self._loading_steps = ['resources', 'entities', 'physics']
        self._current_step = 0

    def get_required_resources(self) -> dict:
        """Specify resources that need to be loaded"""
        # Use paths relative to the current working directory
        return {
            'game_background': 'assets/menu/background.png',  # Use menu background for now
            'player_sprite': 'assets/menu/background.png',    # Use menu background for now
            'jump_sound': 'assets/menu/click.wav',           # Use menu click sound for now
            'game_music': 'assets/menu/music.ogg'            # Use menu music for now
        }

    def load_resources(self):
        """Load all required resources"""
        print("Loading game resources...")
        required_resources = self.get_required_resources()
        total_resources = len(required_resources)
        loaded = 0

        for name, path in required_resources.items():
            try:
                print(f"Loading resource: {path}")
                self.add_resource(name, path)
                loaded += 1
                print(f"Successfully loaded: {path}")
            except Exception as e:
                print(f"Failed to load resource {name}: {e}")

            # Calculate progress based on current step and resource loading
            step_progress = (loaded / total_resources) * 100
            self._loading_progress = (self._current_step * 100 + step_progress) / len(self._loading_steps)

        print(f"Loaded {loaded}/{total_resources} resources")
        self._current_step += 1  # Move to next step
        print(f"Moving to step {self._current_step}")

    def initialize_entities(self):
        """Initialize game entities"""
        print("Initializing entities...")
        # This will be called by subclasses
        self._loading_progress = ((self._current_step * 100) + 50) / len(self._loading_steps)
        self._current_step += 1  # Move to next step
        print(f"Moving to step {self._current_step}")

    def initialize_physics(self):
        """Initialize physics system"""
        print("Initializing physics...")
        # Set up collision system
        self.collision_system.clear()
        self._loading_progress = ((self._current_step * 100) + 50) / len(self._loading_steps)
        self._current_step += 1  # Move to next step
        print(f"Moving to step {self._current_step}")
        
        # Mark as fully loaded after all steps complete
        if self._current_step >= len(self._loading_steps):
            print("All loading steps complete")
            self._is_loaded = True
            self._loading_progress = 100

    def update(self):
        """Update scene with entity processing and collision detection"""
        if not self._is_loaded:
            print(f"Current loading step: {self._current_step}")
            # Continue loading process
            if self._current_step == 0:
                self.load_resources()
            elif self._current_step == 1:
                self.initialize_entities()
            elif self._current_step == 2:
                self.initialize_physics()
            return

        if self.paused:
            return

        # First update all entities using parallel processing
        super().update()
        
        # Then update collision system
        self.collision_system.update(self.entities)

    def on_enter(self, previous_scene):
        """Called when scene becomes active"""
        super().on_enter(previous_scene)  # Call base class on_enter first
        
        # Start background music if available
        if self._is_loaded:  # Only play music when fully loaded
            music = self.get_resource('game_music')
            if music:
                music.play(-1)  # Loop indefinitely

        # Get any persistent data from previous scene
        if self.interface and self.interface.scene_manager:
            last_score = self.interface.scene_manager.get_persistent_data('last_score', 0)
            # Could use this to continue from last score, show high score, etc.

    def on_exit(self):
        """Called when switching to another scene"""
        # Stop background music
        pygame.mixer.music.stop()
        
        # Store any data that should persist
        if self.interface and self.interface.scene_manager:
            self.interface.scene_manager.store_persistent_data('last_score', self.get_score())
        
        super().on_exit()  # Call base class on_exit

    def on_pause(self):
        """Called when another scene is pushed on top"""
        self.paused = True
        pygame.mixer.music.pause()
        super().on_pause()  # Call base class on_pause

    def on_resume(self):
        """Called when scene is resumed (top scene was popped)"""
        self.paused = False
        pygame.mixer.music.unpause()
        super().on_resume()  # Call base class on_resume

    def get_score(self):
        """Get current game score - override in subclasses"""
        return 0

    def cleanup(self):
        """Clean up scene resources"""
        self.collision_system.clear()
        pygame.mixer.music.stop()
        super().cleanup()  # Call base class cleanup

class Player(Entity):
    def __init__(self, x: float = 0, y: float = 0, scene=None):
        super().__init__(x, y)
        self.scene = scene
        
        # Add components - for now just use a red square
        self.renderer = self.add_component(RectangleRenderer(40, 40, (255, 0, 0)))  # Red square
        self.collider = self.add_component(Collider(40, 40))
        physics = self.add_component(Physics(mass=1.0, gravity=0.5, friction=0.3))  # Increased friction
        physics.restitution = 0.0  # No bounce for better platforming feel
        self.physics = physics
        self.controller = self.add_component(KeyboardController(speed=5.0))

        # Set up collision response
        self.collider.set_collision_layer(0)  # Player layer
        self.collider.set_collision_mask(2)   # Collide with platforms (layer 1)
        
    def jump(self):
        """Handle player jump with sound effect"""
        if self.physics.is_grounded and self.scene:
            self.physics.apply_impulse(0, -12.0)  # Upward impulse
            # Play jump sound if available
            jump_sound = self.scene.get_resource('jump_sound')
            if jump_sound:
                jump_sound.play()

class Platform(Entity):
    def __init__(self, x: float, y: float, width: float, height: float, color: tuple):
        super().__init__(x, y)
        
        # Add components
        self.renderer = self.add_component(RectangleRenderer(width, height, color))
        self.collider = self.add_component(Collider(width, height))
        self.physics = self.add_component(Physics())
        
        # Make it static
        self.physics.set_kinematic(True)
        
        # Set up collision
        self.collider.set_collision_layer(1)  # Platform layer
        self.collider.set_collision_mask(1)   # Collide with player (layer 0)

class UIManager(Entity):
    def __init__(self, scene):
        super().__init__(0, 0)
        self.scene = scene
        self.ui = self.add_component(UIComponent())
        self.score = 0
        self.time = 0
        
        # Create pause menu
        self.menu = self.ui.create_menu(10, 10, 200, 300, [
            ("Resume", self.resume_game),
            ("Restart", self.restart_game),
            ("Settings", self.show_settings),
            ("Main Menu", self.return_to_menu),
            ("Exit", self.exit_game)
        ])
        self.menu.background_color = (40, 40, 40)
        self.menu.border_color = (100, 100, 100)
        self.menu.border_width = 2
        self.menu.visible = False  # Hide menu initially
        
        # Create settings dialog (hidden by default)
        self.settings_dialog = self.ui.create_dialog(
            250, 100, 300, 200,
            "Settings",
            "Game settings will go here"
        )
        self.settings_dialog.visible = False
        
        # Create game info panel
        info_panel = self.ui.create_panel(600, 10, 190, 100)
        info_panel.background_color = (40, 40, 40, 180)
        info_panel.border_color = (100, 100, 100)
        info_panel.border_width = 1
        
        # Add labels to info panel
        self.score_label = self.ui.create_label(10, 10, "Score: 0")
        self.time_label = self.ui.create_label(10, 40, "Time: 0")
        info_panel.add_child(self.score_label)
        info_panel.add_child(self.time_label)
        
    def resume_game(self):
        self.menu.visible = False
        if isinstance(self.scene, GameScene):
            self.scene.paused = False
        
    def restart_game(self):
        if self.scene and self.scene.interface:
            self.scene.interface.scene_manager.set_scene("game", transition=True)
        
    def show_settings(self):
        self.settings_dialog.visible = not self.settings_dialog.visible
        
    def return_to_menu(self):
        if self.scene and self.scene.interface:
            self.scene.interface.scene_manager.set_scene("menu", transition=True)
        
    def exit_game(self):
        if self.scene and self.scene.interface:
            self.scene.interface.running = False

    def update(self):
        if not self.scene.paused:
            self.time += 1/60  # Assuming 60 FPS
            self.score_label.text = f"Score: {self.score}"
            self.time_label.text = f"Time: {int(self.time)}s"

class DebugInfo(Entity):
    def __init__(self):
        super().__init__(0, 0)
        self.add_component(DebugInfoComponent())

class DemoScene(GameScene):
    def __init__(self, num_threads: int = None):
        super().__init__(num_threads)
        self.ui_manager = None
        self.player = None
        self.debug_info = None
        
    def initialize_entities(self):
        """Initialize game entities"""
        print("Initializing DemoScene entities...")
        
        # Create UI manager
        self.ui_manager = UIManager(self)
        self.add_entity(self.ui_manager, "ui")
        
        # Create debug info display
        self.debug_info = DebugInfo()
        self.add_entity(self.debug_info, "debug")
        
        # Create player
        self.player = Player(400, 100, self)  # Start from top
        self.add_entity(self.player, "player")

        # Create platforms
        self.create_platform(400, 550, 800, 40, (0, 255, 0))  # Ground
        self.create_platform(200, 400, 200, 20, (0, 200, 0))  # Platform 1
        self.create_platform(600, 300, 200, 20, (0, 200, 0))  # Platform 2
        self.create_platform(400, 200, 200, 20, (0, 200, 0))  # Platform 3

        # Create walls
        self.create_platform(0, 300, 40, 600, (0, 200, 0))    # Left wall
        self.create_platform(800, 300, 40, 600, (0, 200, 0))  # Right wall
        
        # Call parent's initialize_entities to update progress
        super().initialize_entities()

    def create_platform(self, x: float, y: float, width: float, height: float, color: tuple):
        platform = Platform(x, y, width, height, color)
        self.add_entity(platform, "platforms")

    def handle_event(self, event: pygame.event.Event):
        if not self._is_loaded:
            return
            
        super().handle_event(event)
        
        if not self.paused:
            # Handle jumping
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.player:
                    self.player.jump()
                    
        # Handle pause menu
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.ui_manager:
                self.ui_manager.menu.visible = not self.ui_manager.menu.visible
                self.paused = self.ui_manager.menu.visible

    def get_score(self):
        """Get current game score"""
        return self.ui_manager.score if self.ui_manager else 0

    def render(self, screen: pygame.Surface):
        # Draw background
        background = self.get_resource('game_background')
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill((20, 20, 20))
            
        # Render game entities
        super().render(screen)
