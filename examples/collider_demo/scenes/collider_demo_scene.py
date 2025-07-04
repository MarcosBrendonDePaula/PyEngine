import pygame
import math
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.collider import RectCollider, CircleCollider, PolygonCollider
from engine.core.components.physics import Physics
from engine.core.components.rectangle_renderer import RectangleRenderer

class MovableObject(Entity):
    def __init__(self, x: float, y: float, width: float, height: float, color: tuple, name: str, is_static: bool = False):
        super().__init__(x, y)
        self.name = name
        self.is_colliding = False
        
        # Visual representation
        #self.renderer = self.add_component(RectangleRenderer(width, height, color))
        # Physics for movement with collision response
        self.physics = self.add_component(Physics(mass=1.0, gravity=0, friction=0.8))
        self.physics.is_kinematic = is_static  # Static objects are kinematic (not affected by physics)
        self.physics.restitution = 0.5  # Add bounce to collisions
        # Collision detection
        self.collider = self.add_component(RectCollider(width, height))
        self.collider.show_debug = True  # Explicitly enable debug visualization
        self.collider.set_debug_color((255, 0, 0))  # Red collider outline
        
        self.speed = 8.0
        self.knockback_force = 5.0

    def update(self):
        super().update()
        
        # Check collisions with other objects
        if self.scene:
            for entity in self.scene.get_entities_by_group("physics_objects"):
                if entity != self and entity.collider and self.collider.check_collision(entity.collider):
                    self.is_colliding = True
                    entity.is_colliding = True
                    self.on_collision(entity)

    def on_collision(self, other_entity):
        """Handle collision with other entities"""
        if isinstance(other_entity, MovableObject) and not self.physics.is_kinematic:
            # Calculate direction from this object to other object
            direction = pygame.math.Vector2(
                other_entity.position.x - self.position.x,
                other_entity.position.y - self.position.y
            )
            if direction.length() > 0:
                direction.normalize_ip()
                # Apply knockback only if we're not kinematic
                self.physics.apply_impulse(-direction.x * self.knockback_force, 
                                        -direction.y * self.knockback_force)

    def render(self, screen: pygame.Surface, camera_offset=(0, 0)):
        # First render the collider
        if self.collider:
            self.collider.render_debug(screen, camera_offset)
            
        # Then render the entity and components
        super().render(screen, camera_offset)
        
        # Render collision status text
        font = pygame.font.Font(None, 24)
        status = "Colliding!" if self.is_colliding else "No Collision"
        color = (255, 0, 0) if self.is_colliding else (255, 255, 255)
        text = font.render(f"{self.name}: {status}", True, color)
        
        # Position text above the object
        text_pos = (
            self.position.x - text.get_width() // 2 - camera_offset[0],
            self.position.y - 40 - camera_offset[1]
        )
        screen.blit(text, text_pos)
        
        # Reset collision status for next frame
        self.is_colliding = False

class CircleObject(MovableObject):
    def __init__(self, x: float, y: float, radius: float, color: tuple):
        super().__init__(x, y, radius * 2, radius * 2, color, "Circle", is_static=True)
        # Replace rect collider with circle collider
        self.remove_component(self.collider)
        self.collider = self.add_component(CircleCollider(radius))
        self.collider.show_debug = True  # Explicitly enable debug visualization
        self.collider.set_debug_color((255, 0, 0))

class TriangleObject(MovableObject):
    def __init__(self, x: float, y: float, size: float, color: tuple):
        super().__init__(x, y, size, size, color, "Triangle", is_static=True)
        # Replace rect collider with polygon collider
        self.remove_component(self.collider)
        points = [
            (-size/2, size/2),  # Bottom left
            (size/2, size/2),   # Bottom right
            (0, -size/2)        # Top
        ]
        self.collider = self.add_component(PolygonCollider(points))
        self.collider.show_debug = True  # Explicitly enable debug visualization
        self.collider.set_debug_color((255, 0, 0))

class HexagonObject(MovableObject):
    def __init__(self, x: float, y: float, size: float, color: tuple):
        super().__init__(x, y, size, size, color, "Hexagon", is_static=True)
        # Replace rect collider with polygon collider
        self.remove_component(self.collider)
        
        # Create hexagon points
        points = []
        for i in range(6):
            angle = math.pi / 3 * i  # 60 degrees * i
            px = math.cos(angle) * size/2
            py = math.sin(angle) * size/2
            points.append((px, py))
            
        self.collider = self.add_component(PolygonCollider(points))
        self.collider.show_debug = True  # Explicitly enable debug visualization
        self.collider.set_debug_color((255, 0, 0))

class StarObject(MovableObject):
    def __init__(self, x: float, y: float, size: float, color: tuple):
        super().__init__(x, y, size, size, color, "Star", is_static=True)
        # Replace rect collider with polygon collider
        self.remove_component(self.collider)
        
        # Create star points (5 points)
        points = []
        outer_radius = size/2
        inner_radius = size/4
        
        for i in range(10):  # 5 points * 2 vertices per point
            angle = math.pi * i / 5 - math.pi/2
            radius = outer_radius if i % 2 == 0 else inner_radius
            px = math.cos(angle) * radius
            py = math.sin(angle) * radius
            points.append((px, py))
            
        self.collider = self.add_component(PolygonCollider(points))
        self.collider.show_debug = True  # Explicitly enable debug visualization
        self.collider.set_debug_color((255, 0, 0))

class LShapeObject(MovableObject):
    def __init__(self, x: float, y: float, size: float, color: tuple):
        super().__init__(x, y, size, size, color, "L-Shape", is_static=True)
        # Replace rect collider with polygon collider
        self.remove_component(self.collider)
        
        # Create L-shape points
        half_size = size/2
        third_size = size/3
        points = [
            (-half_size, half_size),    # Bottom left
            (-third_size, half_size),   # Bottom middle
            (-third_size, -third_size), # Middle right
            (half_size, -third_size),   # Top right
            (half_size, -half_size),    # Top top
            (-half_size, -half_size),   # Top left
        ]
        self.collider = self.add_component(PolygonCollider(points))
        self.collider.show_debug = True  # Explicitly enable debug visualization
        self.collider.set_debug_color((255, 0, 0))

class Player(MovableObject):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 40, 40, (0, 255, 0), "Player", is_static=False)
    
    def update(self):
        # Handle movement first
        keys = pygame.key.get_pressed()
        dx = dy = 0
        
        if keys[pygame.K_LEFT]:
            dx -= self.speed
        if keys[pygame.K_RIGHT]:
            dx += self.speed
        if keys[pygame.K_UP]:
            dy -= self.speed
        if keys[pygame.K_DOWN]:
            dy += self.speed
            
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            factor = self.speed / (2 ** 0.5)
            dx *= factor / self.speed
            dy *= factor / self.speed
            
        self.physics.set_velocity(dx, dy)
        
        # Then do collision checks
        super().update()

class ColliderDemoScene(BaseScene):
    def __init__(self):
        super().__init__()
        self._is_loaded = True
        self.setup_demo()
        self.rotation = 0

    def setup_demo(self):
        # Create player
        self.player = Player(400, 300)
        self.add_entity(self.player, "physics_objects")

        # Create circle obstacle
        circle = CircleObject(600, 300, 30, (255, 165, 0))  # Orange circle
        self.add_entity(circle, "physics_objects")

        # Create triangle obstacle
        triangle = TriangleObject(200, 300, 50, (255, 0, 255))  # Purple triangle
        self.add_entity(triangle, "physics_objects")

        # Create hexagon obstacle
        hexagon = HexagonObject(400, 150, 60, (255, 255, 0))  # Yellow hexagon
        self.add_entity(hexagon, "physics_objects")

        # Create star obstacle
        star = StarObject(200, 150, 60, (0, 255, 255))  # Cyan star
        self.add_entity(star, "physics_objects")

        # Create L-shape obstacle
        l_shape = LShapeObject(600, 150, 60, (255, 100, 255))  # Pink L-shape
        self.add_entity(l_shape, "physics_objects")

    def render(self, screen: pygame.Surface):
        # Fill background with dark gray
        screen.fill((40, 40, 40))
        
        # First render all entities
        for entity in self.entities:
            if entity.visible:
                renderer = entity.get_component(RectangleRenderer)
                if renderer:
                    renderer.render(screen, (0, 0))

        # Then render all entities again to draw collision text on top
        for entity in self.entities:
            if entity.visible and isinstance(entity, MovableObject):
                entity.render(screen, (0, 0))

        # Add debug text
        font = pygame.font.Font(None, 24)
        texts = [
            "Green Rectangle: Player (Arrow keys to move)",
            "Orange Circle: Static circle collider",
            "Purple Triangle: Static triangle collider",
            "Yellow Hexagon: Static hexagon collider",
            "Cyan Star: Static star collider",
            "Pink L-Shape: Static L-shaped collider",
            f"Active Physics Objects: {len(self.get_entities_by_group('physics_objects'))}"
        ]
        
        y = 10
        for text in texts:
            surface = font.render(text, True, (255, 255, 255))
            pygame.display.get_surface().blit(surface, (10, y))
            y += 25

    def update(self, delta_time: float):
        # Call parent update
        super().update(delta_time)
        
        # Rotate all polygon colliders using actual delta time
        self.rotation += 45 * delta_time  # 45 degrees per second
        for entity in self.entities:
            collider = entity.get_component(PolygonCollider)
            if collider:
                collider.rotate(self.rotation)
