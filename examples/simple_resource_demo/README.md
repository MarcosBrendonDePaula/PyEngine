# Simple Resource Demo

This demo shows how to use the ResourceManager to load and cache resources.

## Features

- Global ResourceManager instance for easy access
- Texture loading and caching
- Simple UI to display loaded textures
- Resource statistics display

## Controls

- Press 1: Load character.png
- Press 2: Load character_sheet.png
- Press 3: Load character.png with a different ID to demonstrate caching

## How to Run

```
python examples/simple_resource_demo/simple_resource_demo.py
```

## Implementation Details

This demo shows a simple implementation of the ResourceManager. The key features demonstrated are:

1. **Global Instance**: Using `ResourceManager.get_instance()` to access the global ResourceManager
2. **Resource Loading**: Loading textures with `resource_manager.load_texture(path)`
3. **Resource Caching**: The ResourceManager automatically caches resources to avoid loading the same resource multiple times
4. **Statistics**: Getting cache statistics with `resource_manager.get_stats()`

## Code Example

```python
# Get the global ResourceManager instance
resource_manager = ResourceManager.get_instance()

# Load a texture
texture = resource_manager.load_texture("assets/character.png")

# Get cache statistics
stats = resource_manager.get_stats()
print(f"Cache: {stats['cache']['total_resources']} resources, {stats['cache']['memory_usage_mb']:.2f}MB used")
