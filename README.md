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

### Example 3: Local Multiplayer Game with Logging
```python
from engine import create_engine
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.rectangle_renderer import RectangleRenderer
from engine.core.components.physics import Physics
from engine.core.components.collider import Collider
from engine.core.components.log_component import LogComponent
import pygame

class GameScene(BaseScene):
    def __init__(self):
        super().__init__()
        
        # Create logger
        logger_entity = Entity(10, 10)
        self.logger = logger_entity.add_component(LogComponent(max_messages=5))
        self.add_entity(logger_entity, "ui")
        
        # Log game start
        self.logger.log("Game Started!", "info", 3.0)
        
        # Create players
        self.player1 = self.create_player(200, 300, (0, 0, 255), 1)
        self.player2 = self.create_player(600, 300, (0, 255, 0), 2)
        
    def create_player(self, x, y, color, player_num):
        player = Player(x, y, color, player_num)
        self.add_entity(player, "players")
        self.logger.log(f"Player {player_num} joined!", "info", 2.0)
        return player
        
    def on_player_hit(self, player_num, damage):
        self.logger.log(f"Player {player_num} took {damage} damage!", "warning", 2.0)
        
    def on_game_over(self, winner):
        self.logger.log(f"Game Over - Player {winner} Wins!", "error")

def main():
    engine = create_engine("Game Demo", 800, 600)
    engine.set_scene("game", GameScene())
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

Features:
- **Multiple Log Levels**: 
  - Info: White text for general information
  - Warning: Yellow text for important notices
  - Error: Red text for critical issues
- **Timed Messages**: Messages can automatically disappear after a specified duration
- **Message History**: Maintains a configurable number of recent messages
- **Visual Customization**:
  - Adjustable font size and line height
  - Customizable colors per log level
  - Configurable background transparency
  - Adjustable padding and layout
- **Scene Integration**: Works seamlessly with the entity-component system
- **Performance Optimized**: Automatically removes expired messages

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
