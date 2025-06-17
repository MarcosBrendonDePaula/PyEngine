# Water Collision Demo

This demo showcases the efficiency of the PyEngine with a water particle simulation that includes collision detection and physics.

## Features

- Water particle simulation with physics
- Collision detection between particles and obstacles
- Resource caching for efficient rendering
- Interactive controls to adjust simulation parameters
- Performance monitoring with FPS display

## Controls

- **Mouse Drag**: Move the particle emitter
- **C Key**: Toggle collider visibility
- **R Key**: Reset obstacles to initial state
- **Space Key**: Add a random obstacle
- **FPS Slider**: Adjust the frame rate limit
- **Particles Slider**: Change the maximum number of particles
- **Spawn Rate Slider**: Adjust how quickly particles are created
- **Gravity Slider**: Control the gravity strength for water particles

## Implementation Details

This demo demonstrates several key features of the PyEngine:

1. **Resource Management**: Uses the global ResourceManager instance for efficient resource handling
2. **Entity-Component System**: Leverages components like Collider, Physics, and ParticleSystem
3. **Collision Detection**: Shows the engine's collision system with different collider types
4. **Physics Simulation**: Demonstrates realistic physics with gravity, friction, and restitution
5. **Performance Optimization**: Shows how the engine handles thousands of entities efficiently

## How to Run

```
python examples/water_collision_demo/water_collision_demo_main.py
```

## Technical Notes

The demo creates two types of entities:

1. **Water Particles**: Each particle is an entity with:
   - CircleCollider for collision detection
   - Physics component for realistic movement
   - Visual representation through the ParticleSystem

2. **Obstacles**: Static or dynamic objects with:
   - RectCollider for collision detection
   - Optional Physics component for movement

The collision system efficiently detects and resolves collisions between particles and obstacles, demonstrating the engine's ability to handle complex simulations with many entities.
