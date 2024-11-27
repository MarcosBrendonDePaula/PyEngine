# PyEngine

A high-performance 2D game engine built with Python and Pygame, featuring multi-core processing, component-based architecture, and a comprehensive UI system.

## Features

### Core Systems
- **Multi-core Processing**: Utilizes parallel processing for entity updates, automatically scaling to available CPU cores
- **Component-based Architecture**: Flexible entity-component system for modular game object creation
- **Scene Management**: Sophisticated scene handling with transitions and loading states
- **Resource Management**: Smart asset loading with reference counting and automatic cleanup
- **Logging System**: Flexible in-game logging component with support for:
  - Multiple log levels (info, warning, error)
  - Timed messages with auto-removal
  - Message history with configurable size
  - Semi-transparent overlay display
  - Color-coded messages by level

### Physics & Collision
- **Physics Engine**: Built-in physics system with:
  - Gravity and mass simulation
  - Force and impulse application
  - Friction and kinematic bodies
  - Velocity and acceleration handling
- **Collision Detection**: Rectangle-based collision system with layers and masks

### User Interface
Comprehensive UI system with 15+ ready-to-use components, featuring dual compatibility with both UIElement and Entity systems:
- **Basic Controls**: 
  - Buttons, Labels, Panels
  - Progress Bars (supports both UI hierarchy and scene-based usage)
  - Labels (supports both UI hierarchy and scene-based usage)
- **Input Elements**: Text Input, Multiline Input, Select, Radio Buttons
- **Layout Components**: Grid, ScrollView, Tabs, TitledPanel
- **Advanced Features**: HTML View, Tooltips, Modal Dialogs, Menus
- **Interactive Elements**: Sliders, Toggles, Image Display

Key UI Features:
- Dual System Integration:
  - Full UIElement functionality (parent-child relationships, hierarchical layout)
  - Full Entity system compatibility (components, scene management)
  - Seamless usage in both UI hierarchies and game scenes
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
from engine.core.ui.progress_bar import ProgressBar

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
        panel.add_child(title)  # Add to UI hierarchy
        
        # Add progress bar
        progress = ProgressBar(10, 60, 280, 20)
        progress.set_colors((0, 255, 0))  # Green progress
        progress.progress = 0.75  # Set to 75%
        panel.add_child(progress)  # Add to UI hierarchy
        
        # Add interactive button
        def on_click():
            print("Button clicked!")
            
        button = Button(10, 90, 280, 40, "Start Game")
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
        # Add physics with gravity and improved settings
        physics = self.add_component(Physics(
            mass=1.0,
            gravity=0.5,
            friction=0.3  # Increased friction for better control
        ))
        physics.restitution = 0.0  # No bounce for better platforming feel
        self.physics = physics
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

### Example 3: Local Multiplayer Game with Logging
```python
from engine import create_engine
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.rectangle_renderer import RectangleRenderer
from engine.core.components.physics import Physics
from engine.core.components.collider import Collider
from engine.core.components.log_component import LogComponent
from engine.core.ui.progress_bar import ProgressBar
import pygame

class Player(Entity):
    def __init__(self, x: float, y: float, color: tuple, controls: dict, player_num: int):
        super().__init__(x, y)
        # Visual representation (colored square)
        self.renderer = self.add_component(RectangleRenderer(40, 40, color))
        # Physics for movement with collision response
        self.physics = self.add_component(Physics(mass=1.0, gravity=0, friction=0.8))
        self.physics.restitution = 0.5  # Add bounce to collisions
        # Collision detection
        self.collider = self.add_component(Collider(40, 40))
        # Store controls configuration
        self.controls = controls
        self.speed = 8.0
        self.health = 100
        self.player_num = player_num
        self.knockback_force = 5.0
        
    def tick(self):
        super().tick()
        # Handle movement
        keys = pygame.key.get_pressed()
        dx = dy = 0
        
        if keys[self.controls['left']]: dx -= self.speed
        if keys[self.controls['right']]: dx += self.speed
        if keys[self.controls['up']]: dy -= self.speed
        if keys[self.controls['down']]: dy += self.speed
            
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            factor = self.speed / (2 ** 0.5)
            dx *= factor / self.speed
            dy *= factor / self.speed
            
        self.physics.set_velocity(dx, dy)
    
    def attack(self):
        hitbox = AttackHitbox(self.position.x + 40, self.position.y, self)
        if self.scene:
            self.scene.add_entity(hitbox, "attacks")
            if self.scene.logger:
                self.scene.logger.log(f"Player {self.player_num} attacked!", "info", 2.0)

class MultiplayerScene(BaseScene):
    def __init__(self):
        super().__init__()
        
        # Create logger
        logger_entity = Entity(10, 10)
        self.logger = logger_entity.add_component(LogComponent(max_messages=5))
        self.add_entity(logger_entity, "ui")
        
        # Create Player 1 (Blue, WASD controls)
        self.player1 = Player(200, 300, (0, 0, 255), {
            'up': pygame.K_w,
            'down': pygame.K_s,
            'left': pygame.K_a,
            'right': pygame.K_d,
            'attack': pygame.K_SPACE
        }, 1)
        self.add_entity(self.player1, "players")
        
        # Create Player 2 (Green, Arrow controls)
        self.player2 = Player(600, 300, (0, 255, 0), {
            'up': pygame.K_UP,
            'down': pygame.K_DOWN,
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT,
            'attack': pygame.K_RETURN
        }, 2)
        self.add_entity(self.player2, "players")
        
        # Create health bars
        self.create_health_displays()
        self.logger.log("Game Started!", "info", 3.0)
    
    def create_health_displays(self):
        # Player 1 health bar (blue)
        self.p1_health = ProgressBar(20, 50, 200, 20)
        self.p1_health.set_colors((0, 0, 255))
        self.add_entity(self.p1_health, "ui")
        
        # Player 2 health bar (green)
        self.p2_health = ProgressBar(580, 50, 200, 20)
        self.p2_health.set_colors((0, 255, 0))
        self.add_entity(self.p2_health, "ui")

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

### Logging System
```python
# Create an entity with logging component
logger_entity = Entity(10, 10)
logger = logger_entity.add_component(LogComponent(max_messages=5))
scene.add_entity(logger_entity, "ui")

# Log messages with different levels and durations
logger.log("Game Started!", "info", 3.0)  # Shows for 3 seconds
logger.log("Player took damage!", "warning")  # Permanent message
logger.log("Game Over!", "error")  # Permanent error message

# Clear all messages
logger.clear()

# Get current messages
messages = logger.get_messages()

# Customize logger appearance
logger.line_height = 20  # Adjust line spacing
logger.padding = 10      # Adjust padding
logger.background_alpha = 160  # Adjust background transparency
logger.colors["info"] = (0, 255, 0)  # Custom color for info messages
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
