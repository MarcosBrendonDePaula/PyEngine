import pygame
from engine.core.scenes.base_scene import BaseScene
from engine.core.resource_manager import ResourceManager

# Import UI helpers
from .ui_helper import create_ui, update_stats_labels, update_preloading_progress

# Import demos
from .demos import texture_loading_demo
from .demos import sprite_sheet_demo
from .demos import transformation_cache_demo
from .demos import memory_management_demo
from .demos import preloading_demo

class ResourceCacheDemoScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.background_color = (30, 30, 30)
        self.resource_manager = ResourceManager()
        self.demo_state = "initial"
        self.load_times = []
        self.current_demo = 0
        self.demo_buttons = []
        self.demo_entities = []
        self.stats = {}
        self.preload_progress = 0
        self.preload_total = 0
        
        self.demo_names = [
            "Texture Loading Cache",
            "Sprite Sheet Cache",
            "Transformation Cache",
            "Memory Management",
            "Preloading"
        ]
        
        self.demo_descriptions = [
            "Loading the same texture multiple times uses the cache",
            "Extracting frames from sprite sheets is cached",
            "Transformed textures (scaled, flipped, etc.) are cached",
            "Resources are automatically unloaded when memory limit is reached",
            "Resources can be preloaded in the background"
        ]
        
        self.demo_functions = [
            texture_loading_demo.run_demo,
            sprite_sheet_demo.run_demo,
            transformation_cache_demo.run_demo,
            memory_management_demo.run_demo,
            preloading_demo.run_demo
        ]
    
    def load_resources(self):
        """Load resources for the demo"""
        print("Loading resources for ResourceCacheDemoScene")
        
        # Create UI elements
        create_ui(self)
        
        # Mark scene as loaded
        self._is_loaded = True
        self._loading_progress = 100
        
        # Load the first demo
        self.load_demo_resources()
        
        print("Resources loaded")
    
    def _on_demo_button_click(self, demo_index):
        """Handle demo button clicks"""
        if self.current_demo != demo_index:
            self.current_demo = demo_index
            self.description_label.set_text(self.demo_descriptions[demo_index])
            self.load_demo_resources()
    
    def load_demo_resources(self):
        """Load resources for the current demo"""
        # Clear any existing demo entities
        for entity in self.demo_entities:
            self.remove_entity(entity)
        self.demo_entities = []
        
        # Clear cache
        self.resource_manager.clear_cache()
        
        # Reset stats
        for label in self.stats_labels:
            label.set_text("")
        
        # Call the appropriate demo function
        if 0 <= self.current_demo < len(self.demo_functions):
            self.demo_functions[self.current_demo](self)
    
    def _update_stats_labels(self):
        """Update the stats labels with current information"""
        update_stats_labels(self)
    
    def update(self, delta_time):
        """Update the scene"""
        super().update(delta_time)
        
        # Update preloading progress display
        if self.demo_state == "preloading":
            update_preloading_progress(self)
    
    def render(self, screen):
        """Render the scene"""
        # Fill background with our custom color instead of the default black
        screen.fill(self.background_color)
        
        # Render preloading progress bar if in preloading state
        if self.demo_state == "preloading":
            progress_pct = self.preload_progress / self.preload_total
            pygame.draw.rect(screen, (50, 50, 50), (300, 230, 200, 20))
            pygame.draw.rect(screen, (100, 200, 100), (300, 230, 200 * progress_pct, 20))
        
        # Use the BaseScene's render method to render all entities
        super().render(screen)
