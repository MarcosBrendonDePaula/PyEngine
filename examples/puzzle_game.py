import pygame
import math
import multiprocessing as mp
from engine import create_engine
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.collider import CircleCollider, PolygonCollider
from engine.core.components.physics import Physics
from engine.core.components.rectangle_renderer import RectangleRenderer
from engine.core.components.ui.label import Label

class PuzzlePiece(Entity):
    def __init__(self, x: float, y: float, shape_type: str, size: float, color: tuple):
        super().__init__(x, y)
        self.shape_type = shape_type
        self.is_colliding = False
        self.color = color
        
        # Add physics
        self.physics = self.add_component(Physics(
            mass=1.0,
            gravity=0,
            friction=0.8
        ))
        
        # Visual representation
        self.renderer = self.add_component(RectangleRenderer(size, size, color))
        
        # Add shape-specific collider
        if shape_type == "circle":
            self.collider = self.add_component(CircleCollider(size/2))
        elif shape_type == "triangle":
            points = [
                (-size/2, size/2),  # Bottom left
                (size/2, size/2),   # Bottom right
                (0, -size/2)        # Top
            ]
            self.collider = self.add_component(PolygonCollider(points))
        elif shape_type == "star":
            points = self._create_star_points(size)
            self.collider = self.add_component(PolygonCollider(points))
        
        self.collider.show_debug = True
        self.collider.set_debug_color((255, 0, 0))
        
        self.speed = 5.0
    
    def _create_star_points(self, size):
        points = []
        for i in range(10):
            angle = math.pi * i / 5 - math.pi/2
            radius = size/2 if i % 2 == 0 else size/4
            px = math.cos(angle) * radius
            py = math.sin(angle) * radius
            points.append((px, py))
        return points
    
    def tick(self):
        super().tick()
        
        # Check collisions
        if self.scene:
            for entity in self.scene.get_entities_by_group("pieces"):
                if entity != self and entity.collider and self.collider.check_collision(entity.collider):
                    self.is_colliding = True
                    entity.is_colliding = True
    
    def render(self, screen: pygame.Surface, camera_offset=(0, 0)):
        # Render shape
        if self.renderer:
            self.renderer.render(screen, camera_offset)
        
        # Render collider for debug
        if self.collider:
            self.collider.render_debug(screen, camera_offset)
        
        # Render shape type text
        font = pygame.font.Font(None, 24)
        status = "Colliding!" if self.is_colliding else "No Collision"
        color = (255, 0, 0) if self.is_colliding else (255, 255, 255)
        text = font.render(f"{self.shape_type}: {status}", True, color)
        
        text_pos = (
            self.position.x - text.get_width() // 2,
            self.position.y - 40
        )
        screen.blit(text, text_pos)
        
        # Reset collision status
        self.is_colliding = False

class PuzzleScene(BaseScene):
    def __init__(self):
        super().__init__()
        self._is_loaded = True
        self.selected_piece = None
        self._create_puzzle_pieces()
        self._create_ui()
    
    def _create_puzzle_pieces(self):
        # Circle piece (blue)
        self.add_entity(PuzzlePiece(200, 300, "circle", 40, (0, 0, 255)), "pieces")
        # Triangle piece (green)
        self.add_entity(PuzzlePiece(400, 300, "triangle", 50, (0, 255, 0)), "pieces")
        # Star piece (yellow)
        self.add_entity(PuzzlePiece(600, 300, "star", 60, (255, 255, 0)), "pieces")
    
    def _create_ui(self):
        # Add title
        title = Label(10, 10, "Puzzle Game - Click and drag shapes!")
        title.set_text_color((255, 255, 255))
        self.add_entity(title, "ui")
        
        # Add instructions
        instructions = [
            "Left click to select a piece",
            "Move mouse to drag",
            "Release to drop",
            "Watch for collisions!"
        ]
        
        y = 40
        for instruction in instructions:
            label = Label(10, y, instruction)
            label.set_text_color((200, 200, 200))
            self.add_entity(label, "ui")
            y += 25
    
    def handle_event(self, event: pygame.event.Event):
        super().handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Get mouse position
            mouse_pos = pygame.mouse.get_pos()
            
            # Check if we clicked on a piece
            for entity in self.get_entities_by_group("pieces"):
                if isinstance(entity, PuzzlePiece):
                    # Simple distance check for selection
                    dx = mouse_pos[0] - entity.position.x
                    dy = mouse_pos[1] - entity.position.y
                    if math.sqrt(dx*dx + dy*dy) < 30:  # 30px selection radius
                        self.selected_piece = entity
                        break
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.selected_piece = None
        
        elif event.type == pygame.MOUSEMOTION and self.selected_piece:
            # Move selected piece to mouse position
            self.selected_piece.position.x = event.pos[0]
            self.selected_piece.position.y = event.pos[1]
    
    def render(self, screen: pygame.Surface):
        # Fill background
        screen.fill((40, 40, 40))
        
        # Render all entities
        for entity in self.entities:
            if entity.visible:
                entity.render(screen)

def main():
    # Get CPU cores for processing
    cpu_count = mp.cpu_count()
    num_threads = max(1, int(cpu_count * 0.75))
    
    # Create engine
    engine = create_engine(
        title="PyEngine Puzzle Game",
        width=800,
        height=600,
        num_threads=num_threads
    )
    
    # Create and set scene
    scene = PuzzleScene()
    engine.set_scene("puzzle", scene)
    
    # Run game
    engine.run()

if __name__ == "__main__":
    main()
