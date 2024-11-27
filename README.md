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
Comprehensive UI system with 15+ ready-to-use components:
- **Basic Controls**: Buttons, Labels, Panels, Progress Bars
- **Input Elements**: Text Input, Multiline Input, Select, Radio Buttons
- **Layout Components**: Grid, ScrollView, Tabs, TitledPanel
- **Advanced Features**: HTML View, Tooltips, Modal Dialogs, Menus
- **Interactive Elements**: Sliders, Toggles, Image Display

## Installation

1. Ensure you have Python 3.7+ installed
2. Install the required dependencies:
```bash
pip install pygame
```

## Quick Start

### Basic Game Setup
```python
from engine import create_engine
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.physics import Physics
from engine.core.components.collider import Collider

# Create a game entity
class Player(Entity):
    def __init__(self, x: float = 0, y: float = 0):
        super().__init__(x, y)
        # Add physics with gravity
        self.physics = self.add_component(Physics(
            mass=1.0,
            gravity=0.5,
            friction=0.1
        ))
        # Add collision detection
        self.collider = self.add_component(Collider(40, 40))
        self.collider.set_collision_layer(0)

# Create a game scene
class GameScene(BaseScene):
    def __init__(self):
        super().__init__()
        # Create player
        self.player = Player(400, 300)
        self.add_entity(self.player, "player")

# Run the game
def main():
    engine = create_engine("My Game", 800, 600)
    engine.set_scene("game", GameScene())
    engine.run()

if __name__ == "__main__":
    main()
```

### UI System Usage
```python
from engine.core.ui.panel import Panel
from engine.core.ui.button import Button
from engine.core.ui.label import Label
from engine.core.ui.modal import MessageBox

class MenuScene(BaseScene):
    def __init__(self):
        super().__init__()
        
        # Create main panel
        panel = Panel(20, 20, 300, 400)
        
        # Add title
        title = Label(10, 10, "Main Menu")
        panel.add_child(title)
        
        # Add button with click handler
        def start_game():
            MessageBox("Game", "Starting new game...").show()
            
        button = Button(10, 50, 200, 40, "Start Game")
        button.on_click = start_game
        panel.add_child(button)
        
        # Add panel to scene
        self.add_entity(panel, "ui")
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

## Advanced Features

### Physics System
```python
# Create a physics-enabled entity
physics = entity.add_component(Physics(
    mass=1.0,    # Entity mass
    gravity=0.5, # Gravity scale
    friction=0.1 # Surface friction
))

# Apply forces and impulses
physics.apply_force(0, -10)  # Continuous force
physics.apply_impulse(5, 0)  # Instant force
physics.set_velocity(3, 0)   # Direct velocity

# Configure physics behavior
physics.set_kinematic(True)  # Ignore forces
physics.terminal_velocity = 10.0  # Max speed
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

### Advanced UI Components
```python
# Create tabs with content
tabs = Tabs(20, 20, 760, 560)
basic_panel = tabs.add_tab("basic", "Basic Controls")
advanced_panel = tabs.add_tab("advanced", "Advanced")

# Create data grid
grid = Grid(20, 20, 700, 200, [
    GridColumn("ID", "id", 80),
    GridColumn("Name", "name", 200)
])
grid.set_data([
    {"id": 1, "name": "Player 1"},
    {"id": 2, "name": "Player 2"}
])

# Create HTML view
html_view = HTMLView(20, 20, 400, 200)
html_view.set_html("""
    <h1>Title</h1>
    <p>Formatted <b>text</b></p>
""")
```

## Performance Tips

1. Use entity groups for organized parallel processing
2. Leverage the built-in multi-core processing for heavy computations
3. Properly manage resources using the ResourceLoader
4. Use sprite sheets for efficient rendering
5. Implement culling for off-screen entities
6. Utilize the scene manager's loading system for smooth transitions
7. Take advantage of the component system for modular and reusable code

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

This project is open source and available under the MIT License.
