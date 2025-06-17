import pygame
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.texture_renderer import TextureRenderer
from engine.core.components.ui.label import Label
from engine.core.resource_manager import ResourceManager

class SimpleResourceScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.background_color = (30, 30, 30)
        # Get the global ResourceManager instance
        self.resource_manager = ResourceManager.get_instance()
        self.entities = []
        self.labels = []
        
    def load_resources(self):
        """Load resources for the demo"""
        print("Loading resources for SimpleResourceScene")
        
        # Create title label
        title_label = Label(
            x=20, 
            y=20, 
            text="Simple Resource Demo",
            font_size=24
        )
        title_label.set_text_color((255, 255, 255))
        self.add_entity(title_label)
        
        # Create instruction label
        instruction_label = Label(
            x=20,
            y=60,
            text="Press 1-3 to load different textures",
            font_size=18
        )
        instruction_label.set_text_color((200, 200, 200))
        self.add_entity(instruction_label)
        
        # Create stats labels
        self.stats_label = Label(
            x=20,
            y=500,
            text="",
            font_size=16
        )
        self.stats_label.set_text_color((200, 200, 200))
        self.add_entity(self.stats_label)
        
        # Create entity for displaying textures
        self.display_entity = Entity()
        self.display_entity.position.x = 400
        self.display_entity.position.y = 300
        self.texture_renderer = TextureRenderer()
        self.display_entity.add_component(self.texture_renderer)
        self.add_entity(self.display_entity)
        
        # Load initial texture
        self.load_texture("assets/character.png")
        
        # Mark scene as loaded
        self._is_loaded = True
        self._loading_progress = 100
        print("Resources loaded")
    
    def load_texture(self, path):
        """Load a texture using the ResourceManager"""
        # Load the texture
        texture = self.resource_manager.load_texture(path)
        
        if texture:
            # Set the texture on the renderer
            self.texture_renderer.set_texture(texture)
            
            # Update stats
            stats = self.resource_manager.get_stats()
            self.stats_label.set_text(
                f"Cache: {stats['cache']['total_resources']} resources, "
                f"{stats['cache']['memory_usage_mb']:.2f}MB used"
            )
    
    def handle_event(self, event):
        """Handle input to change textures"""
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.load_texture("assets/character.png")
            elif event.key == pygame.K_2:
                self.load_texture("assets/character_sheet.png")
            elif event.key == pygame.K_3:
                # Load the same texture with a different ID to show caching
                self.resource_manager.load_texture("assets/character.png", "character_copy")
                self.load_texture("assets/character.png")
    
    def render(self, screen):
        """Render the scene"""
        # Fill background with our custom color
        screen.fill(self.background_color)
        
        # Use the BaseScene's render method to render all entities
        super().render(screen)
