import pygame
import math
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.directional_light import DirectionalLight
from engine.core.components.rectangle_renderer import RectangleRenderer

class Wall(Entity):
    def __init__(self, points: list, color: tuple = (80, 80, 90)):
        # Calculate center position from points
        center_x = sum(x for x, y in points) / len(points)
        center_y = sum(y for x, y in points) / len(points)
        super().__init__(center_x, center_y)
        
        self.points = points
        self.color = color
        
        # Add rectangle renderer for visualization
        width = max(x for x, y in points) - min(x for x, y in points)
        height = max(y for x, y in points) - min(y for x, y in points)
        self.renderer = self.add_component(RectangleRenderer(width, height, color))
    
    def render(self, screen: pygame.Surface, camera_offset=(0, 0)):
        # Draw the wall polygon
        pygame.draw.polygon(screen, self.color, self.points)
        super().render(screen, camera_offset)

class DirectionalLightDemo(BaseScene):
    def __init__(self):
        super().__init__()
        self._is_loaded = True
        self.background_color = (10, 10, 15)  # Darker background
        
        # Track time for light rotation
        self.last_time = pygame.time.get_ticks()
        self.auto_rotate = True
        self.rotation_speed = 30  # Slower rotation for better visibility
        
        # Light movement speed
        self.light_speed = 5.0
        
        self.setup_scene()
    
    def setup_scene(self):
        # Create walls and obstacles
        self.walls = [
            # Buildings
            Wall([(100, 100), (200, 100), (200, 200), (100, 200)]),  # Square building
            Wall([(300, 150), (350, 100), (400, 150), (350, 200)]),  # Diamond building
            Wall([(500, 100), (600, 100), (600, 300), (500, 300)]),  # Tall building
            
            # Trees/poles
            Wall([(150, 300), (170, 300), (170, 350), (150, 350)]),
            Wall([(250, 250), (270, 250), (270, 300), (250, 300)]),
            Wall([(450, 200), (470, 200), (470, 250), (450, 250)]),
            
            # Triangular structures
            Wall([(600, 350), (650, 300), (700, 350)]),
            Wall([(100, 400), (150, 350), (200, 400)]),
            
            # Ground obstacles
            Wall([(300, 400), (400, 400), (400, 450), (300, 450)]),
            Wall([(500, 400), (550, 400), (575, 450), (525, 450)])
        ]
        
        # Add walls to scene
        for wall in self.walls:
            self.add_entity(wall, "walls")
        
        # Create directional light at center of screen
        self.light_entity = Entity(400, 300)  # Start at center
        self.light = DirectionalLight(
            color=(255, 230, 180),  # Warm sunlight color
            intensity=1.5,  # Higher intensity
            angle=45
        )
        # Update light with wall polygons
        wall_polygons = [wall.points for wall in self.walls]
        self.light.update_obstacles(wall_polygons)
        
        self.light_entity.add_component(self.light)
        self.add_entity(self.light_entity, "lights")
    
    def update(self):
        # Calculate dt
        current_time = pygame.time.get_ticks()
        dt = (current_time - self.last_time) / 1000.0  # Convert to seconds
        self.last_time = current_time
        
        # Update light rotation if auto-rotate is enabled
        if self.auto_rotate and hasattr(self, 'light'):
            current_angle = self.light.angle
            new_angle = (current_angle + self.rotation_speed * dt) % 360
            self.light.set_angle(new_angle)
        
        # Handle keyboard input for light movement
        keys = pygame.key.get_pressed()
        dx = dy = 0
        
        if keys[pygame.K_a]:  # Move left
            dx = -self.light_speed
        if keys[pygame.K_d]:  # Move right
            dx = self.light_speed
        if keys[pygame.K_w]:  # Move up
            dy = -self.light_speed
        if keys[pygame.K_s]:  # Move down
            dy = self.light_speed
            
        # Update light position
        if dx != 0 or dy != 0:
            self.light_entity.position.x += dx
            self.light_entity.position.y += dy
            # Keep light within screen bounds
            self.light_entity.position.x = max(0, min(800, self.light_entity.position.x))
            self.light_entity.position.y = max(0, min(600, self.light_entity.position.y))
        
        super().update()
    
    def render(self, screen: pygame.Surface):
        # Fill background
        screen.fill(self.background_color)
        
        # Render all entities
        for entity in self.entities:
            if entity.visible:
                entity.render(screen, (0, 0))
        
        # Draw debug information
        if pygame.font.get_init():
            font = pygame.font.Font(None, 24)
            texts = [
                "Controls:",
                "WASD: Move light",
                "Left/Right Arrow: Rotate light manually",
                "Space: Toggle auto-rotation",
                "Escape: Exit",
                "",
                f"Light Position: ({int(self.light_entity.position.x)}, {int(self.light_entity.position.y)})",
                f"Light Angle: {int(self.light.angle)}°",
                f"Auto Rotate: {'On' if self.auto_rotate else 'Off'}"
            ]
            
            y = 10
            for text in texts:
                surface = font.render(text, True, (200, 200, 200))
                screen.blit(surface, (10, y))
                y += 25
    
    def handle_event(self, event):
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Toggle auto-rotation
                self.auto_rotate = not self.auto_rotate
            
            elif event.key == pygame.K_LEFT:
                # Rotate light counterclockwise
                if hasattr(self, 'light'):
                    self.auto_rotate = False
                    current_angle = self.light.angle
                    self.light.set_angle(current_angle - 15)
            
            elif event.key == pygame.K_RIGHT:
                # Rotate light clockwise
                if hasattr(self, 'light'):
                    self.auto_rotate = False
                    current_angle = self.light.angle
                    self.light.set_angle(current_angle + 15)
