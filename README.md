# PyEngine

A high-performance 2D game engine built with Python and Pygame, featuring multi-core processing, advanced lighting, physics simulation, and a comprehensive UI system.

## Core Features

### Multi-Core Processing
- Automatic CPU core detection and utilization
- Parallel entity processing for improved performance
- Configurable thread count (defaults to 75% of available cores)
- Efficient workload distribution

### Scene Management
- Scene-based game organization
- Smooth scene transitions
- Resource loading management
- Persistent data between scenes

### Entity-Component System
- Flexible component-based architecture
- Hot-swappable components
- Entity grouping and layering
- Component dependency management

## Physics & Collision System

### Physics Engine
- Gravity and mass simulation
- Force and impulse application
- Friction and restitution
- Velocity and acceleration handling
- Kinematic body support

### Advanced Collision Detection
Multiple collider types with debug visualization:
- Rectangle Colliders
- Circle Colliders
- Polygon Colliders
  - Triangle
  - Hexagon
  - Star
  - L-Shape
  - Custom Shapes
- Collision layers and masks
- Rotation support for polygon colliders
- Collision response and knockback

## Lighting System

### Light Components
- Dynamic light sources
- Color and intensity control
- Customizable light radius
- Multiple light types:
  - Point lights
  - Directional lights
  - Area lights

### Advanced Features
- Ray tracing for realistic light behavior
- Shadow casting
- Light color blending
- Dynamic obstacle handling
- Real-time light updates
- Warm/cool light temperature

## User Interface System

### Basic Controls
- Labels: Text display with customizable fonts
- Buttons: Interactive clickable elements
- ProgressBar: Visual progress indication
- Slider: Value selection along a range
- Toggle: On/off state switches
- Input: Text input fields
- MultilineInput: Multi-line text editing

### Layout Components
- Panel: Basic container with styling
- TitledPanel: Panel with header text
- Grid: Grid-based layout system
- ScrollView: Scrollable content container
- Tabs: Tabbed interface organization

### Advanced UI Features
- HTMLView: Basic HTML rendering
- Tooltip: Hover information display
- Modal: Popup dialog system
- Menu: Dropdown and context menus
- Image: Image display component
- RadioButton: Option selection
- Select: Dropdown selection
- InputSelect: Searchable dropdown

### UI Architecture
- Hierarchical component system
- Event propagation
- Automatic layout management
- Style inheritance
- Component state management

## Game Examples

### 1. Local Multiplayer Combat Game
```python
from engine import create_engine
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.physics import Physics
from engine.core.components.collider import Collider
from engine.core.components.log_component import LogComponent
from engine.core.components.ui.progress_bar import ProgressBar

class Player(Entity):
    def __init__(self, x: float, y: float, color: tuple, controls: dict, player_num: int):
        super().__init__(x, y)
        # Add physics for movement
        self.physics = self.add_component(Physics(mass=1.0, gravity=0, friction=0.8))
        self.physics.restitution = 0.5  # Add bounce
        
        # Add collision
        self.collider = self.add_component(Collider(40, 40))
        
        # Setup player properties
        self.controls = controls
        self.speed = 8.0
        self.health = 100
        self.player_num = player_num
        
    def tick(self):
        super().tick()
        # Handle movement based on controls
        keys = pygame.key.get_pressed()
        dx = dy = 0
        
        if keys[self.controls['left']]: dx -= self.speed
        if keys[self.controls['right']]: dx += self.speed
        if keys[self.controls['up']]: dy -= self.speed
        if keys[self.controls['down']]: dy += self.speed
            
        self.physics.set_velocity(dx, dy)

class MultiplayerScene(BaseScene):
    def __init__(self):
        super().__init__()
        
        # Add logging system
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
        self._create_health_bars()
        self.logger.log("Game Started!", "info", 3.0)

def main():
    engine = create_engine("Local Multiplayer Demo", 800, 600)
    engine.set_scene("game", MultiplayerScene())
    engine.run()
```

### 2. Platformer with Dynamic Lighting
```python
from engine import create_engine
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.physics import Physics
from engine.core.components.collider import RectCollider
from engine.core.components.light_component import LightComponent

class Player(Entity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        # Physics with gravity
        self.physics = self.add_component(Physics(
            mass=1.0,
            gravity=0.5,
            friction=0.3
        ))
        self.physics.restitution = 0.0  # No bounce
        
        # Collision
        self.collider = self.add_component(RectCollider(40, 40))
        
        # Player light
        self.light = self.add_component(LightComponent(
            color=(255, 220, 150),  # Warm light
            intensity=1.2,
            radius=200
        ))
    
    def jump(self):
        if self.physics.is_grounded:
            self.physics.apply_impulse(0, -12.0)

class Platform(Entity):
    def __init__(self, x: float, y: float, width: float, height: float):
        super().__init__(x, y)
        # Static physics
        self.physics = self.add_component(Physics())
        self.physics.set_kinematic(True)
        
        # Collision
        self.collider = self.add_component(RectCollider(width, height))

class PlatformerScene(BaseScene):
    def __init__(self):
        super().__init__()
        # Create player
        self.player = Player(400, 300)
        self.add_entity(self.player, "player")
        
        # Create platforms
        self._create_platforms()
        
        # Add ambient light
        ambient = Entity(400, 300)
        ambient.add_component(LightComponent(
            color=(100, 100, 150),
            intensity=0.5,
            radius=800
        ))
        self.add_entity(ambient, "lights")
    
    def _create_platforms(self):
        # Ground
        self.add_entity(Platform(400, 550, 800, 40), "platforms")
        # Floating platforms
        self.add_entity(Platform(200, 400, 200, 20), "platforms")
        self.add_entity(Platform(600, 300, 200, 20), "platforms")
        self.add_entity(Platform(400, 200, 200, 20), "platforms")

def main():
    engine = create_engine("Platformer Demo", 800, 600)
    engine.set_scene("game", PlatformerScene())
    engine.run()
```

### 3. Puzzle Game with Advanced Colliders
```python
from engine import create_engine
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.collider import CircleCollider, PolygonCollider
from engine.core.components.physics import Physics

class PuzzlePiece(Entity):
    def __init__(self, x: float, y: float, shape_type: str, size: float):
        super().__init__(x, y)
        # Add physics
        self.physics = self.add_component(Physics(
            mass=1.0,
            gravity=0,
            friction=0.8
        ))
        
        # Add shape-specific collider
        if shape_type == "circle":
            self.collider = self.add_component(CircleCollider(size))
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
    
    def _create_star_points(self, size):
        points = []
        for i in range(10):
            angle = math.pi * i / 5 - math.pi/2
            radius = size/2 if i % 2 == 0 else size/4
            px = math.cos(angle) * radius
            py = math.sin(angle) * radius
            points.append((px, py))
        return points

class PuzzleScene(BaseScene):
    def __init__(self):
        super().__init__()
        # Create puzzle pieces
        self._create_puzzle_pieces()
        
        # Create target zones
        self._create_target_zones()
    
    def _create_puzzle_pieces(self):
        # Circle piece
        self.add_entity(PuzzlePiece(200, 300, "circle", 40), "pieces")
        # Triangle piece
        self.add_entity(PuzzlePiece(400, 300, "triangle", 50), "pieces")
        # Star piece
        self.add_entity(PuzzlePiece(600, 300, "star", 60), "pieces")

def main():
    engine = create_engine("Puzzle Demo", 800, 600)
    engine.set_scene("game", PuzzleScene())
    engine.run()
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

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

This project is open source and available under the MIT License.
