import pygame
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.ui_component import UIComponent

class MenuUI(Entity):
    def __init__(self, scene):
        super().__init__(0, 0)
        print("Creating MenuUI")
        self.scene = scene
        self.ui = self.add_component(UIComponent())
        
        # Set root panel size to match screen
        self.ui.root.width = 800
        self.ui.root.height = 600
        self.ui.root.background_color = (20, 20, 20)  # Dark background
        
        # Create title
        self.title = self.ui.create_label(300, 100, "PyEngine Demo", font_size=48)
        self.title.set_text_color((255, 255, 0))  # Yellow text
        self.title.background_color = (40, 40, 40)  # Dark background
        self.title.border_color = (100, 100, 100)
        self.title.border_width = 2
        
        # Create centered menu panel
        menu_width = 200
        menu_height = 300
        menu_x = 400 - menu_width // 2  # Center horizontally
        menu_y = 250  # Below title
        
        # Create menu with click sound
        def button_clicked(callback):
            def wrapper():
                click_sound = self.scene.get_resource('menu_click')
                if click_sound:
                    click_sound.play()
                callback()
            return wrapper
        
        self.menu = self.ui.create_menu(
            menu_x, menu_y, 
            menu_width, menu_height,
            [
                ("Play", button_clicked(self.on_play_clicked)),
                ("Settings", button_clicked(self.show_settings)),
                ("Exit", button_clicked(self.exit_game))
            ]
        )
        
        # Style the menu
        self.menu.background_color = (40, 40, 40)
        self.menu.border_color = (100, 100, 100)
        self.menu.border_width = 2
        
        # Create settings dialog (hidden by default)
        self.settings_dialog = self.ui.create_dialog(
            250, 150, 300, 200,
            "Settings",
            "Game settings will go here"
        )
        self.settings_dialog.visible = False
        print("MenuUI created successfully")
        
    def on_play_clicked(self):
        print("Play button clicked")
        # Store any persistent data needed in game scene
        if self.scene.interface and self.scene.interface.scene_manager:
            self.scene.interface.scene_manager.store_persistent_data('last_score', 0)
            
            # Change to game scene if it exists
            if 'game' in self.scene.interface.scene_manager._scenes:
                print("Using existing game scene")
                self.scene.interface.scene_manager.set_scene('game', transition=True)
            else:
                print("Creating new game scene")
                # Add game scene if it doesn't exist
                from examples.scenes.game_scene import DemoScene
                game_scene = DemoScene()
                self.scene.interface.scene_manager.add_scene('game', game_scene)
                self.scene.interface.scene_manager.set_scene('game', transition=True)
        
    def show_settings(self):
        self.settings_dialog.visible = not self.settings_dialog.visible
        
    def exit_game(self):
        if self.scene and self.scene.interface:
            self.scene.interface.running = False

    def render(self, screen: pygame.Surface, camera_offset=(0, 0)):
        """Override render to ignore camera offset for UI"""
        if not self.visible:
            return
            
        # Render all components without camera offset
        for component in self.components.values():
            if component.enabled:
                component.render(screen, (0, 0))  # Always use (0, 0) for UI

class MenuScene(BaseScene):
    def __init__(self):
        super().__init__()
        print("MenuScene initialized")
        self.menu_ui = None
        self._is_loaded = False  # Start as not loaded
        
    def get_required_resources(self) -> dict:
        """Specify resources that need to be loaded"""
        return {
            'menu_background': 'examples/assets/menu/background.png',
            'menu_click': 'examples/assets/menu/click.wav',
            'menu_music': 'examples/assets/menu/music.ogg'
        }
        
    def load_resources(self):
        """Load all required resources"""
        print("Loading menu resources...")
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

            self._loading_progress = (loaded / total_resources) * 100

        print(f"Loaded {loaded}/{total_resources} resources")
        self._is_loaded = True
        
        # After resources are loaded, create the UI
        if self._is_loaded and not self.menu_ui:
            self.create_ui()
        
    def create_ui(self):
        """Create menu UI after resources are loaded"""
        # Create and add menu UI
        self.menu_ui = MenuUI(self)
        self.add_entity(self.menu_ui, "ui")  # Explicitly add to "ui" group
        print(f"Added MenuUI to scene, total entities: {len(self.entities)}")
        
        # Start background music
        music = self.get_resource('menu_music')
        if music:
            music.play(-1)  # Loop indefinitely
        
    def on_initialize(self):
        """One-time initialization"""
        print("MenuScene on_initialize called")
        # Initialize pygame mixer if using sound
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
    def on_enter(self, previous_scene):
        """Called when scene becomes active"""
        print("MenuScene on_enter called")
        super().on_enter(previous_scene)
        # Start background music if available
        music = self.get_resource('menu_music')
        if music:
            music.play(-1)  # Loop indefinitely
            
    def on_exit(self):
        """Called when switching to another scene"""
        print("MenuScene on_exit called")
        # Stop background music
        music = self.get_resource('menu_music')
        if music:
            music.stop()
        super().on_exit()
            
    def on_pause(self):
        """Called when another scene is pushed on top"""
        print("MenuScene on_pause called")
        # Pause background music
        music = self.get_resource('menu_music')
        if music:
            music.pause()
        super().on_pause()
            
    def on_resume(self):
        """Called when scene is resumed (top scene was popped)"""
        print("MenuScene on_resume called")
        # Unpause background music
        music = self.get_resource('menu_music')
        if music:
            music.unpause()
        super().on_resume()
    
    def render(self, screen: pygame.Surface):
        """Render the scene"""
        # Draw background
        background = self.get_resource('menu_background')
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill((20, 20, 20))
        
        # Use base scene's render which handles camera offsets properly
        super().render(screen)
        
        # Debug: Draw rectangles around UI elements
        if self.menu_ui and self.menu_ui.ui:
            pygame.draw.rect(screen, (255, 0, 0), 
                           (self.menu_ui.ui.root.x, self.menu_ui.ui.root.y,
                            self.menu_ui.ui.root.width, self.menu_ui.ui.root.height), 1)
        
    def cleanup(self):
        """Clean up scene resources"""
        music = self.get_resource('menu_music')
        if music:
            music.stop()
        super().cleanup()
