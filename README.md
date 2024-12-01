# PyEngine

A high-performance 2D game engine built with Python and Pygame, featuring multi-core processing, advanced lighting, physics simulation, sprite animation, and a comprehensive UI system.

## Features

### Core Systems

#### Multi-Core Processing
- Automatic CPU core detection and utilization
- Parallel entity processing for improved performance
- Configurable thread count (defaults to 75% of available cores)
- Efficient workload distribution

#### Scene Management
- Scene-based game organization
- Smooth scene transitions
- Resource loading management
- Persistent data between scenes

#### Entity-Component System
- Flexible component-based architecture
- Hot-swappable components
- Entity grouping and layering
- Component dependency management

### Animation System

#### Sprite Animation
- Lane-based sprite sheet animation
- Support for variable frame sizes
- Multiple animations per row support
- Custom lane width limits
- Animation state management:
  - Continuous animation states
  - Animation queuing
  - Frame callbacks
  - Direction-aware sprite flipping
  - Animation speed control

### Physics System

#### Physics Engine
- Gravity and mass simulation
- Force and impulse application
- Friction and restitution
- Velocity and acceleration handling
- Kinematic body support

#### Collision Detection
Multiple collider types with debug visualization:
- Rectangle Colliders
- Circle Colliders
- Polygon Colliders:
  - Triangle
  - Hexagon
  - Star
  - L-Shape
  - Custom Shapes
- Collision layers and masks
- Rotation support for polygon colliders
- Collision response and knockback

### Lighting System

#### Light Components
- Dynamic light sources
- Color and intensity control
- Customizable light radius
- Multiple light types:
  - Point lights
  - Directional lights
  - Area lights

#### Advanced Features
- Ray tracing for realistic light behavior
- Shadow casting
- Light color blending
- Dynamic obstacle handling
- Real-time light updates
- Warm/cool light temperature

### UI System

#### Basic Controls
- Labels: Text display with customizable fonts
- Buttons: Interactive clickable elements
- ProgressBar: Visual progress indication
- Slider: Value selection along a range
- Toggle: On/off state switches
- Input: Text input fields
- MultilineInput: Multi-line text editing

#### Layout Components
- Panel: Basic container with styling
- TitledPanel: Panel with header text
- Grid: Grid-based layout system
- ScrollView: Scrollable content container
- Tabs: Tabbed interface organization

#### Advanced UI Features
- HTMLView: Basic HTML rendering
- Tooltip: Hover information display
- Modal: Popup dialog system
- Menu: Dropdown and context menus
- Image: Image display component
- RadioButton: Option selection
- Select: Dropdown selection
- InputSelect: Searchable dropdown

#### UI Architecture
- Hierarchical component system
- Event propagation
- Automatic layout management
- Style inheritance
- Component state management

## Usage Examples

### 1. Character Animation
```python
from engine import create_engine
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.sprite_animation import SpriteAnimation

class Character(Entity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.sprite_animation = self.add_component(SpriteAnimation())
        
        # Load sprite sheet
        self.sprite_animation.load_sprite_sheet("assets/character.png")
        
        # Add idle animation (5 frames, 100x160)
        self.sprite_animation.create_animation_from_lane(
            name="idle",
            start_x=0,          # Start X position
            start_y=0,          # First row
            frame_width=100,    # Frame width
            frame_height=160,   # Frame height
            frame_count=5,      # Number of frames
            frame_duration=0.2, # Duration per frame
            loop=True          # Loop animation
        )
        
        # Add walk animation (5 frames, 100x160)
        self.sprite_animation.create_animation_from_lane(
            name="walk",
            start_x=0,         # Start X position
            start_y=160,       # Second row
            frame_width=100,   # Frame width
            frame_height=160,  # Frame height
            frame_count=5,     # Number of frames
            frame_duration=0.15,
            loop=True
        )
        
        # Add jump animation (3 frames, 150x500)
        self.sprite_animation.create_animation_from_lane(
            name="jump",
            start_x=0,         # Start X position
            start_y=320,       # Third row
            frame_width=150,   # Frame width
            frame_height=500,  # Frame height
            frame_count=3,     # Number of frames
            frame_duration=0.1,
            loop=False
        )
        
        # Start with idle animation
        self.sprite_animation.play("idle")
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.sprite_animation.set_flip(False, False)  # Face left
            self.sprite_animation.play("walk")
            self.position.x -= 2
        elif keys[pygame.K_RIGHT]:
            self.sprite_animation.set_flip(True, False)   # Face right
            self.sprite_animation.play("walk")
            self.position.x += 2
        else:
            self.sprite_animation.play("idle")

class AnimationScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.character = Character(400, 300)
        self.add_entity(self.character)
    
    def update(self):
        super().update()
        self.character.handle_input()

def main():
    engine = create_engine("Animation Demo", 800, 600)
    engine.set_scene("game", AnimationScene())
    engine.run()
```

### 2. Physics and Collision
```python
from engine.core.components.physics import Physics
from engine.core.components.collider import Collider

class Player(Entity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        # Add physics with gravity
        self.physics = self.add_component(Physics(
            mass=1.0,
            gravity=0.5,
            friction=0.3
        ))
        self.physics.restitution = 0.0  # No bounce
        
        # Add collision
        self.collider = self.add_component(Collider(40, 40))
```

### 3. Dynamic Lighting
```python
from engine.core.components.light_component import LightComponent

class Torch(Entity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        # Add flickering light
        self.light = self.add_component(LightComponent(
            color=(255, 200, 100),  # Warm color
            intensity=1.2,
            radius=150
        ))
```

### 4. User Interface
```python
from engine.core.components.ui.panel import Panel
from engine.core.components.ui.button import Button
from engine.core.components.ui.label import Label

class MenuScene(BaseScene):
    def __init__(self):
        super().__init__()
        # Create menu panel
        menu = Panel(200, 100, 400, 300)
        menu.add_child(Label(10, 10, "Main Menu"))
        menu.add_child(Button(10, 50, "Start Game", self.start_game))
        menu.add_child(Button(10, 100, "Options", self.show_options))
        self.add_ui_element(menu)
```

## Project Structure

```
PyEngine/
├── engine/
│   ├── core/
│   │   ├── components/
│   │   │   ├── physics.py
│   │   │   ├── collider.py
│   │   │   ├── light_component.py
│   │   │   ├── sprite_animation.py
│   │   │   └── ui/
│   │   ├── scenes/
│   │   ├── entity.py
│   │   └── input.py
│   └── __init__.py
├── tests/
│   ├── scenes/
│   │   ├── sprite_animation_demo.py
│   │   ├── physics_demo.py
│   │   └── lighting_demo.py
│   └── demo_mains/
├── assets/
└── README.md
```

## Installation

```bash
pip install pygame
```

## Performance Tips

1. Use entity groups for organized parallel processing
2. Leverage multi-core processing for heavy computations
3. Implement culling for off-screen entities
4. Use sprite sheets for efficient rendering
5. Properly manage resources using ResourceLoader
6. Group UI elements appropriately
7. Optimize collision layers and masks
8. Use appropriate light radii and update frequencies
9. Use lane-based sprite animation for efficient memory usage
10. Set appropriate frame durations for smooth animations

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

This project is open source and available under the MIT License.
