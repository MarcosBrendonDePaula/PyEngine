# PyEngine - 2D Game Engine

A multi-core 2D game engine built on top of Pygame, designed for high-performance game development with parallel processing capabilities, extensive UI system, and component-based architecture.

## Features

- **Multi-core Processing**: Utilizes parallel processing for entity updates
- **Scene Management**: Organized game state handling with scene-based architecture
- **Entity Component System**: Flexible and modular component-based architecture
- **Physics & Collision**: Built-in physics and collision detection system
- **Resource Management**: Efficient asset loading and handling
- **Comprehensive UI System**: Rich set of UI components
- **Camera System**: Smooth camera movement and viewport management

## Installation

1. Ensure you have Python 3.7+ installed
2. Install the required dependencies:
```bash
pip install pygame
```

## Quick Start

### Creating a Basic Game

```python
from engine import create_engine
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.rectangle_renderer import RectangleRenderer
from engine.core.components.physics import Physics
from engine.core.components.collider import Collider

# Create a player entity
class Player(Entity):
    def __init__(self, x: float = 0, y: float = 0):
        super().__init__(x, y)
        # Add visual representation
        self.renderer = self.add_component(RectangleRenderer(40, 40, (255, 0, 0)))
        # Add physics and collision
        self.physics = self.add_component(Physics(mass=1.0, gravity=0.5))
        self.collider = self.add_component(Collider(40, 40))

# Create a game scene
class GameScene(BaseScene):
    def __init__(self):
        super().__init__()
        # Create and add player
        self.player = Player(400, 300)
        self.add_entity(self.player, "player")

# Create and run the game
def main():
    engine = create_engine("My Game", 800, 600)
    game_scene = GameScene()
    engine.interface.set_scene(game_scene)
    engine.run()

if __name__ == "__main__":
    main()
```

### Creating UI Interfaces

```python
from engine.core.ui.button import Button
from engine.core.ui.label import Label
from engine.core.ui.panel import Panel
from engine.core.ui.modal import MessageBox
from engine.core.ui.grid import Grid, GridColumn

# Create a menu panel
panel = Panel(x=20, y=20, width=300, height=400)

# Add a label
label = Label(x=10, y=10, text="Main Menu")
panel.add_child(label)

# Add a button with click handler
def on_click():
    MessageBox("Success", "Button clicked!").show()

button = Button(x=10, y=50, width=200, height=40, text="Click Me")
button.on_click = on_click
panel.add_child(button)

# Create a data grid
columns = [
    GridColumn("ID", "id", 80),
    GridColumn("Name", "name", 200),
    GridColumn("Score", "score", 100)
]

grid = Grid(x=10, y=100, width=280, height=200, columns=columns)
grid.set_data([
    {"id": 1, "name": "Player 1", "score": 100},
    {"id": 2, "name": "Player 2", "score": 200}
])
panel.add_child(grid)
```

### Using the Component System

```python
from engine.core.entity import Entity
from engine.core.components.physics import Physics
from engine.core.components.collider import Collider
from engine.core.components.keyboard_controller import KeyboardController

class GameEntity(Entity):
    def __init__(self, x: float = 0, y: float = 0):
        super().__init__(x, y)
        
        # Add physics component
        self.physics = self.add_component(Physics(
            mass=1.0,
            gravity=0.5,
            friction=0.1
        ))
        
        # Add collision component
        self.collider = self.add_component(Collider(
            width=40,
            height=40
        ))
        self.collider.set_collision_layer(0)  # Set collision layer
        self.collider.set_collision_mask(1)   # Set collision mask
        
        # Add keyboard control
        self.controller = self.add_component(KeyboardController(
            speed=5.0
        ))
```

### Resource Management

```python
class GameScene(BaseScene):
    def get_required_resources(self) -> dict:
        return {
            'background': 'assets/background.png',
            'player_sprite': 'assets/player.png',
            'jump_sound': 'assets/jump.wav',
            'music': 'assets/music.ogg'
        }
    
    def on_enter(self, previous_scene):
        super().on_enter(previous_scene)
        # Play background music
        music = self.get_resource('music')
        if music:
            music.play(-1)  # Loop indefinitely
```

### Advanced UI Features

```python
from engine.core.ui.html_view import HTMLView
from engine.core.ui.multiline_input import MultilineInput
from engine.core.ui.tabs import Tabs
from engine.core.ui.menu import Menu, MenuItem

# Create HTML view
html_view = HTMLView(x=20, y=20, width=400, height=200)
html_view.set_html("""
    <h1>Welcome</h1>
    <p>This is a <b>formatted</b> text with <i>HTML support</i>.</p>
""")

# Create multiline text input
text_input = MultilineInput(x=20, y=240, width=400, height=150)
text_input.set_text("Type multiple lines here...\nSupports scrolling and selection.")

# Create tabbed interface
tabs = Tabs(x=20, y=20, width=600, height=400)
basic_panel = tabs.add_tab("basic", "Basic Controls")
advanced_panel = tabs.add_tab("advanced", "Advanced Controls")

# Create dropdown menu
menu_items = [
    MenuItem("File", submenu=[
        MenuItem("New", lambda: print("New")),
        MenuItem("Open", lambda: print("Open"))
    ]),
    MenuItem("Edit", submenu=[
        MenuItem("Cut", lambda: print("Cut")),
        MenuItem("Copy", lambda: print("Copy"))
    ])
]
menu = Menu(x=20, y=20, items=menu_items)
```

## Performance Tips

1. Use entity groups for organized processing
2. Leverage parallel processing for heavy computations
3. Implement object pooling for frequently created/destroyed entities
4. Use sprite sheets for efficient rendering
5. Implement culling for off-screen entities
6. Utilize the grid system for complex UI layouts
7. Pre-load resources using ResourceLoader

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

This project is open source and available under the MIT License.
