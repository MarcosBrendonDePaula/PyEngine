from engine import create_engine
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.rectangle_renderer import RectangleRenderer
from engine.core.components.physics import Physics
from engine.core.components.collider import Collider
from engine.core.ui.progress_bar import ProgressBar
import pygame

class Player(Entity):
    def __init__(self, x: float, y: float, color: tuple, controls: dict):
        super().__init__(x, y)
        # Visual representation (colored square)
        self.renderer = self.add_component(RectangleRenderer(40, 40, color))
        # Physics for movement
        self.physics = self.add_component(Physics(
            mass=1.0,
            friction=0.1
        ))
        self.physics.gravity = 0  # No gravity for top-down movement
        # Collision detection
        self.collider = self.add_component(Collider(40, 40))
        # Store controls configuration
        self.controls = controls
        self.speed = 5.0
        self.health = 100
        
    def handle_event(self, event: pygame.event.Event):
        super().handle_event(event)
        # Handle attacks
        if event.type == pygame.KEYDOWN:
            if event.key == self.controls['attack']:
                self.attack()
    
    def tick(self):
        super().tick()
        # Handle movement
        keys = pygame.key.get_pressed()
        dx = dy = 0
        
        if keys[self.controls['left']]:
            dx -= self.speed
        if keys[self.controls['right']]:
            dx += self.speed
        if keys[self.controls['up']]:
            dy -= self.speed
        if keys[self.controls['down']]:
            dy += self.speed
            
        self.physics.set_velocity(dx, dy)
    
    def attack(self):
        # Create attack hitbox in front of player
        hitbox = AttackHitbox(
            self.position.x + 40, 
            self.position.y,
            self
        )
        if self.scene:
            self.scene.add_entity(hitbox, "attacks")
    
    def take_damage(self, amount: int):
        self.health -= amount
        if self.health <= 0 and self.scene:
            self.scene.player_defeated(self)

class AttackHitbox(Entity):
    def __init__(self, x: float, y: float, owner: Player):
        super().__init__(x, y)
        # Red rectangle for attack
        self.renderer = self.add_component(RectangleRenderer(30, 30, (255, 0, 0)))
        self.collider = self.add_component(Collider(30, 30))
        self.owner = owner
        self.lifetime = 10  # Frames the attack lasts
        
    def tick(self):
        super().tick()
        # Remove after lifetime
        self.lifetime -= 1
        if self.lifetime <= 0 and self.scene:
            self.scene.remove_entity(self)
        
        # Check for hits
        if self.scene:
            for entity in self.scene.get_entities_by_group("players"):
                if entity != self.owner:  # Don't hit self
                    if self.collider.check_collision(entity.collider):
                        entity.take_damage(10)
                        self.scene.remove_entity(self)
                        break

class MultiplayerScene(BaseScene):
    def __init__(self):
        super().__init__()
        
        # Create Player 1 (Blue, WASD controls)
        self.player1 = Player(200, 300, (0, 0, 255), {
            'up': pygame.K_w,
            'down': pygame.K_s,
            'left': pygame.K_a,
            'right': pygame.K_d,
            'attack': pygame.K_SPACE
        })
        self.add_entity(self.player1, "players")
        
        # Create Player 2 (Green, Arrow controls)
        self.player2 = Player(600, 300, (0, 255, 0), {
            'up': pygame.K_UP,
            'down': pygame.K_DOWN,
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT,
            'attack': pygame.K_RETURN
        })
        self.add_entity(self.player2, "players")
        
        # Create UI for health display
        self.create_health_displays()
    
    def create_health_displays(self):
        # Player 1 health bar (blue)
        self.p1_health = ProgressBar(20, 20, 200, 20)
        self.p1_health.set_colors((0, 0, 255))  # Blue progress
        self.add_entity(self.p1_health, "ui")
        
        # Player 2 health bar (green)
        self.p2_health = ProgressBar(580, 20, 200, 20)
        self.p2_health.set_colors((0, 255, 0))  # Green progress
        self.add_entity(self.p2_health, "ui")
    
    def update(self):
        super().update()
        # Update health bars
        self.p1_health.progress = self.player1.health / 100
        self.p2_health.progress = self.player2.health / 100
    
    def player_defeated(self, player):
        from engine.core.ui.modal import MessageBox
        
        winner = "Player 1" if player == self.player2 else "Player 2"
        MessageBox("Game Over", f"{winner} Wins!").show()
        
        # Reset after 2 seconds
        import pygame
        pygame.time.set_timer(pygame.USEREVENT, 2000)  # 2000ms = 2s
    
    def handle_event(self, event):
        super().handle_event(event)
        # Handle reset timer
        if event.type == pygame.USEREVENT:
            pygame.time.set_timer(pygame.USEREVENT, 0)  # Cancel timer
            self.__init__()  # Reset scene

# Run the game
def main():
    engine = create_engine("Local Multiplayer Demo", 800, 600)
    engine.set_scene("game", MultiplayerScene())
    engine.run()

if __name__ == "__main__":
    main()
