# PyEngine

A high-performance 2D game engine built with Python and Pygame, featuring multi-core processing, component-based architecture, and a comprehensive UI system.

## Features

### Core Systems
- **Multi-core Processing**: Utilizes parallel processing for entity updates, automatically scaling to available CPU cores
- **Component-based Architecture**: Flexible entity-component system for modular game object creation
- **Scene Management**: Sophisticated scene handling with transitions and loading states
- **Resource Management**: Smart asset loading with reference counting and automatic cleanup

### Physics & Collision
- **Physics Engine**: Built-in physics system with:
  - Gravity and mass simulation
  - Force and impulse application
  - Friction and kinematic bodies
  - Velocity and acceleration handling
- **Collision Detection**: Rectangle-based collision system with layers and masks

### User Interface
Comprehensive UI system with 15+ ready-to-use components, all fully integrated with the Entity system:
- **Basic Controls**: Buttons, Labels, Panels, Progress Bars
- **Input Elements**: Text Input, Multiline Input, Select, Radio Buttons
- **Layout Components**: Grid, ScrollView, Tabs, TitledPanel
- **Advanced Features**: HTML View, Tooltips, Modal Dialogs, Menus
- **Interactive Elements**: Sliders, Toggles, Image Display

Key UI Features:
- Full Entity system integration (components, scene management, etc.)
- Hierarchical layout system with parent-child relationships
- Automatic positioning and scaling
- Event handling and propagation
- Customizable styling and theming

## Installation

1. Ensure you have Python 3.7+ installed
2. Install the required dependencies:
```bash
pip install pygame
```

## Quick Start

### Example 1: Basic UI Usage
```python
from engine import create_engine
from engine.core.scenes.base_scene import BaseScene
from engine.core.ui.panel import Panel
from engine.core.ui.button import Button
from engine.core.ui.label import Label

class MenuScene(BaseScene):
    def __init__(self):
        super().__init__()
        
        # Create main panel
        panel = Panel(20, 20, 300, 400)
        panel.set_style(
            background_color=(50, 50, 50),
            border_color=(255, 255, 255),
            border_width=2
        )
        
        # Add title label
        title = Label(10, 10, "Main Menu", font_size=32)
        title.set_text_color((255, 255, 255))
        panel.add_child(title)
        
        # Add interactive button
        def on_click():
            print("Button clicked!")
            
        button = Button(10, 60, 280, 40, "Start Game")
        button.on_click = on_click
        panel.add_child(button)
        
        # Add panel to scene
        self.add_entity(panel, "ui")

def main():
    engine = create_engine("UI Demo", 800, 600)
    engine.set_scene("menu", MenuScene())
    engine.run()

if __name__ == "__main__":
    main()
```

### Example 2: Platform Game
```python
from engine import create_engine
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.rectangle_renderer import RectangleRenderer
from engine.core.components.physics import Physics
from engine.core.components.collider import Collider
from engine.core.components.keyboard_controller import KeyboardController
import pygame

# Create player entity
class Player(Entity):
    def __init__(self, x: float = 0, y: float = 0):
        super().__init__(x, y)
        # Red square for player
        self.renderer = self.add_component(RectangleRenderer(40, 40, (255, 0, 0)))
        # Add physics with gravity
        self.physics = self.add_component(Physics(
            mass=1.0,
            gravity=0.5,
            friction=0.1
        ))
        # Add collision
        self.collider = self.add_component(Collider(40, 40))
        self.collider.set_collision_layer(0)  # Player layer
        self.collider.set_collision_mask(1)   # Collide with platforms
        # Add keyboard control
        self.controller = self.add_component(KeyboardController(speed=5.0))
        
    def jump(self):
        if self.physics.is_grounded:
            self.physics.apply_impulse(0, -12.0)  # Upward impulse

# Create platform entity
class Platform(Entity):
    def __init__(self, x: float, y: float, width: float, height: float):
        super().__init__(x, y)
        # Green rectangle for platform
        self.renderer = self.add_component(RectangleRenderer(width, height, (0, 255, 0)))
        # Add collision
        self.collider = self.add_component(Collider(width, height))
        self.collider.set_collision_layer(1)  # Platform layer
        # Make it static
        self.physics = self.add_component(Physics())
        self.physics.set_kinematic(True)

# Create game scene
class PlatformScene(BaseScene):
    def __init__(self):
        super().__init__()
        # Create player
        self.player = Player(400, 300)
        self.add_entity(self.player, "player")
        
        # Create platforms
        # Ground
        self.add_entity(Platform(400, 550, 800, 40), "platforms")
        # Floating platforms
        self.add_entity(Platform(200, 400, 200, 20), "platforms")
        self.add_entity(Platform(600, 300, 200, 20), "platforms")
        self.add_entity(Platform(400, 200, 200, 20), "platforms")
    
    def handle_event(self, event):
        super().handle_event(event)
        # Handle jumping with space bar
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.player.jump()

# Run the game
def main():
    engine = create_engine("Platform Game", 800, 600)
    engine.set_scene("game", PlatformScene())
    engine.run()

if __name__ == "__main__":
    main()
```

### Example 3: Local Multiplayer Game
```python
from engine import create_engine
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.rectangle_renderer import RectangleRenderer
from engine.core.components.physics import Physics
from engine.core.components.collider import Collider
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
        from engine.core.ui.label import Label
        
        # Player 1 health
        self.p1_health = Label(20, 20, "P1: 100")
        self.add_entity(self.p1_health, "ui")
        
        # Player 2 health
        self.p2_health = Label(700, 20, "P2: 100")
        self.add_entity(self.p2_health, "ui")
    
    def update(self):
        super().update()
        # Update health displays
        self.p1_health.text = f"P1: {self.player1.health}"
        self.p2_health.text = f"P2: {self.player2.health}"
    
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
```

### Example 4: UI with Entity Integration
```python
from engine import create_engine
from engine.core.scenes.base_scene import BaseScene
from engine.core.ui.label import Label
from engine.core.components.physics import Physics

class PhysicsLabel(Label):
    def __init__(self, x: int, y: int, text: str):
        super().__init__(x, y, text)
        # Add physics to make the label fall
        self.physics = self.add_component(Physics(
            mass=1.0,
            gravity=0.5
        ))

class PhysicsScene(BaseScene):
    def __init__(self):
        super().__init__()
        # Create physics-enabled labels
        for i in range(5):
            label = PhysicsLabel(100 + i * 100, 0, f"Label {i}")
            self.add_entity(label, "ui")

def main():
    engine = create_engine("Physics UI Demo", 800, 600)
    engine.set_scene("demo", PhysicsScene())
    engine.run()

if __name__ == "__main__":
    main()
```

## Advanced Features

### UI System Integration
```python
# Create a UI element with physics
label = Label(100, 100, "Physics Label")
physics = label.add_component(Physics(mass=1.0))

# Add custom components to UI elements
class CustomBehavior(Component):
    def tick(self):
        # Custom update logic
        pass

label.add_component(CustomBehavior())

# UI elements in the scene system
scene.add_entity(label, "ui")  # Add to UI group
scene.add_entity(label, "physics")  # Add to physics group too
```

### Scene Management
```python
# Create and manage scenes
engine.add_scene("menu", MenuScene())
engine.add_scene("game", GameScene())

# Switch scenes with transition
engine.set_scene("game", transition=True)

# Share data between scenes
scene_manager.store_persistent_data("score", 100)
score = scene_manager.get_persistent_data("score", 0)
```

### Resource Management
```python
class GameScene(BaseScene):
    def get_required_resources(self) -> dict:
        return {
            'player': 'assets/player.png',
            'background': 'assets/background.png',
            'music': 'assets/music.ogg'
        }
    
    def on_enter(self, previous_scene):
        super().on_enter(previous_scene)
        # Access loaded resources
        background = self.get_resource('background')
        music = self.get_resource('music')
        if music:
            music.play(-1)  # Loop music
```

## Performance Tips

1. Use entity groups for organized parallel processing
2. Leverage the built-in multi-core processing for heavy computations
3. Properly manage resources using the ResourceLoader
4. Use sprite sheets for efficient rendering
5. Implement culling for off-screen entities
6. Utilize the scene manager's loading system for smooth transitions
7. Take advantage of the component system for modular and reusable code
8. Group UI elements appropriately in scenes for optimal updating

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

This project is open source and available under the MIT License.
