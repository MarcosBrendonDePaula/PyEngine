# Resource Cache Demo

This demo showcases the advanced resource caching system implemented in the PyEngine game engine. It demonstrates various features of the caching system and how they improve performance and memory usage.

## Features Demonstrated

1. **Texture Loading Cache**: Shows how loading the same texture multiple times uses the cache to improve performance.
2. **Sprite Sheet Cache**: Demonstrates how extracting frames from sprite sheets is cached for better performance.
3. **Transformation Cache**: Shows how transformed textures (scaled, flipped, etc.) are cached to avoid redundant processing.
4. **Memory Management**: Demonstrates the automatic memory management system that unloads resources when memory limits are reached.
5. **Asynchronous Preloading**: Shows how resources can be preloaded in the background while the game continues to run.

## How to Run

```bash
python resource_cache_demo.py
```

## How to Use

- Click on the buttons on the left side to switch between different demos.
- Each demo shows performance metrics and cache statistics.
- The demo compares the loading time of resources with and without caching.

## Implementation Details

The resource caching system is implemented in the `ResourceManager` class, which provides:

- Centralized resource loading and caching
- Reference counting for automatic resource management
- Transformation caching for optimized rendering
- Memory usage tracking and automatic cleanup
- Asynchronous loading capabilities
- Preloading groups for scene transitions

The system is designed to be thread-safe and efficient, making it suitable for games with many assets and limited memory resources.
