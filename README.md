# PyEngine - 2D Game Engine

A multi-core 2D game engine built on top of Pygame, designed for high-performance game development with parallel processing capabilities.

## Features

- **Multi-core Processing**: Utilizes parallel processing for entity updates
- **Scene Management**: Organized game state handling with scene-based architecture
- **Entity System**: Flexible entity base class with encapsulated tick and render processing
- **Input Management**: Centralized input handling for keyboard and mouse
- **Camera System**: Smooth camera movement and viewport management
- **Sprite System**: Easy-to-use sprite management with rotation and scaling
- **Component-based Architecture**: Modular design for easy extension

## Installation

1. Ensure you have Python 3.7+ installed
2. Install the required dependencies:
```bash
pip install pygame
```

## Quick Start

```python
from engine import create_engine, Scene, Sprite

# Create a custom scene
class GameScene(Scene):
    def __init__(self):
        super().__init__()
        self.player = Sprite(400, 300)  # Create a player sprite
        self.add_entity(self.player, "player")

    def update(self):
        # Handle game logic here
        super().update()  # Update all entities in parallel

# Create and run the game
def main():
    engine = create_engine("My Game", 800, 600)
    game_scene = GameScene()
    engine.interface.set_scene(game_scene)
    engine.run()

if __name__ == "__main__":
    main()
```

## Core Components

### Engine
The main engine class that initializes and manages all core systems.

### Interface
Handles window management and the main game loop.

### Scene
Manages game states and entities with parallel processing capabilities.

### Entity
Base class for all game objects with built-in physics properties.

### Sprite
Extended entity class for handling 2D graphics with rotation and scaling.

### Camera
Manages viewport and follows targets with smooth movement.

### Input
Centralized input handling system for keyboard and mouse events.

## Advanced Usage

### Creating Custom Entities

```python
from engine import Entity

class CustomEntity(Entity):
    def __init__(self, x: float = 0, y: float = 0):
        super().__init__(x, y)
        
    def tick(self):
        # Custom update logic
        super().tick()
        
    def render(self, screen, camera_offset=(0, 0)):
        # Custom rendering logic
        super().render(screen, camera_offset)
```

### Scene Management

```python
class MenuScene(Scene):
    def __init__(self):
        super().__init__()
        # Initialize menu items
        
    def handle_event(self, event):
        # Handle menu interactions
        pass

# Switch scenes
engine.interface.set_scene(MenuScene())
```

### Camera Control

```python
# Set camera target
engine.camera.set_target(player_entity)

# Set camera bounds
engine.camera.set_bounds(0, 0, world_width, world_height)

# Adjust camera zoom
engine.camera.zoom = 1.5
```

## Performance Tips

1. Use entity groups for organized processing
2. Leverage parallel processing for heavy computations
3. Implement object pooling for frequently created/destroyed entities
4. Use sprite sheets for efficient rendering
5. Implement culling for off-screen entities

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

This project is open source and available under the MIT License.
