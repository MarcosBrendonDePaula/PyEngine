import pygame
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.light_component import LightComponent
from engine.core.components.keyboard_controller import KeyboardController

class LightDemoScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.background_color = (2, 2, 5)  # Even darker background
        
        # Simple wall layout for demonstrating raytracing
        self.walls = [
            # Room boundaries
            [(100, 100), (700, 100)],  # Top wall
            [(700, 100), (700, 500)],  # Right wall
            [(700, 500), (100, 500)],  # Bottom wall
            [(100, 500), (100, 100)],  # Left wall
            
            # Some angled walls for interesting reflections
            [(300, 200), (400, 300)],  # Diagonal wall 1
            [(500, 200), (400, 300)],  # Diagonal wall 2
            
            # A box in the corner
            [(550, 350), (650, 350), (650, 450), (550, 450)]
        ]
        
        self._create_player_light()
        self._create_static_light()
    
    def _create_player_light(self):
        """Create a player-controlled light source"""
        player = Entity(400, 300)
        
        # Add keyboard control
        controller = KeyboardController(speed=3.0)
        player.add_component(controller)
        
        # Add light with raytracing
        light = LightComponent(
            color=(255, 220, 150),  # Warm light
            intensity=1.5,  # Increased intensity
            radius=300  # Increased radius
        )
        player.add_component(light)
        self.player_light = light
        
        self.add_entity(player)

    def _create_static_light(self):
        """Create a static light source"""
        static_light = Entity(200, 200)
        
        # Add light with different color
        light = LightComponent(
            color=(150, 200, 255),  # Cool light
            intensity=1.2,
            radius=250
        )
        static_light.add_component(light)
        
        self.add_entity(static_light)
    
    def tick(self):
        """Update scene logic"""
        super().tick()
        
        # Update obstacles for all lights
        for entity in self.entities:
            light = entity.get_component(LightComponent)
            if light:
                light.update_obstacles(self.walls)
    
    def render(self, screen):
        """Render the scene"""
        screen.fill(self.background_color)
        
        # Draw walls
        for wall in self.walls:
            if len(wall) == 2:  # Line
                pygame.draw.line(screen, (40, 40, 50), wall[0], wall[1], 3)
            else:  # Polygon
                pygame.draw.polygon(screen, (40, 40, 50), wall)
        
        # Render all entities (lights)
        for entity in self.entities:
            entity.render(screen)
    
    def handle_event(self, event):
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Toggle light color
                if hasattr(self, 'player_light'):
                    light = self.player_light
                    if light.color[0] > 200:  # If warm
                        light.color = (150, 200, 255)  # Cool
                    else:
                        light.color = (255, 220, 150)  # Warm
