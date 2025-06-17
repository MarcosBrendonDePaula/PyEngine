import pygame
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.ui_component import UIComponent

class LoadingUI(Entity):
    def __init__(self, scene):
        super().__init__(0, 0)
        self.scene = scene
        self.ui = self.add_component(UIComponent())
        
        # Set root panel size to match screen
        self.ui.root.width = 800
        self.ui.root.height = 600
        self.ui.root.background_color = (20, 20, 20)
        
        # Create loading text
        self.loading_text = self.ui.create_label(
            400, 250,  # Centered position
            "Loading...",
            font_size=36
        )
        self.loading_text.set_text_color((255, 255, 255))
        
        # Create progress text
        self.progress_text = self.ui.create_label(
            400, 350,  # Below loading text
            "0%",
            font_size=24
        )
        self.progress_text.set_text_color((200, 200, 200))
        
    def update_progress(self, progress: float):
        """Update the loading progress display"""
        self.progress_text.text = f"{int(progress)}%"
        
    def render(self, screen: pygame.Surface, camera_offset=(0, 0)):
        """Render the loading UI"""
        if not self.visible:
            return
            
        # Draw progress bar background
        bar_width = 400
        bar_height = 20
        bar_x = (800 - bar_width) // 2
        bar_y = 300
        pygame.draw.rect(screen, (50, 50, 50), 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Draw progress bar fill
        fill_width = (bar_width * self.scene._loading_progress) // 100
        if fill_width > 0:
            pygame.draw.rect(screen, (0, 255, 0), 
                           (bar_x, bar_y, fill_width, bar_height))
            
        # Render UI components
        for component in self.components.values():
            if component.enabled:
                component.render(screen, (0, 0))

class LoadingScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.loading_ui = None
        self._target_scene = None
        self._is_loaded = True  # Loading scene is always ready
        self._loading_progress = 0
        
    def set_target_scene(self, scene_name: str):
        """Set the scene to transition to after loading"""
        print(f"Setting target scene to: {scene_name}")
        self._target_scene = scene_name
        
    def on_initialize(self):
        """Initialize the loading scene"""
        print("Initializing loading scene")
        self.loading_ui = LoadingUI(self)
        self.add_entity(self.loading_ui, "ui")
        
    def update(self, delta_time=0):
        """Update loading progress and handle scene transition"""
        super().update(delta_time)
        
        if self._target_scene and self.interface and self.interface.scene_manager:
            target = self.interface.scene_manager._scenes.get(self._target_scene)
            if target:
                print(f"Target scene loading progress: {target._loading_progress}%")
                # Update progress based on target scene's loading state
                self._loading_progress = target._loading_progress
                
                # Update UI
                if self.loading_ui:
                    self.loading_ui.update_progress(self._loading_progress)
                
                # Check if target scene is loaded
                if target._is_loaded:
                    print(f"Target scene {self._target_scene} is loaded, transitioning...")
                    # Switch to target scene without transition effect
                    self.interface.scene_manager._change_scene(self._target_scene)
                    self._target_scene = None
                    self._loading_progress = 0
                else:
                    # Continue loading process
                    target.update(delta_time)
                
    def render(self, screen: pygame.Surface):
        """Render the loading scene"""
        # Fill background
        screen.fill((20, 20, 20))
        
        # Use base scene's render which handles entities properly
        super().render(screen)
