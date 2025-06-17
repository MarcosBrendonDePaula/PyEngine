import time
from engine.core.resource_manager import ResourceManager

def run_demo(scene):
    """Demo showing memory management"""
    scene.demo_state = "running"
    scene.load_times = []
    
    # Load multiple textures to fill the cache
    textures_loaded = 0
    start_time = time.time()
    
    # Create a small resource manager with a low memory limit for demo purposes
    small_resource_manager = ResourceManager(max_memory_mb=1)  # 1MB limit
    
    # Load the same texture multiple times with different IDs to fill the cache
    base_texture_path = "assets/character.png"
    
    for i in range(50):
        resource_id = f"demo_texture_{i}"
        texture = small_resource_manager.load_texture(base_texture_path, resource_id)
        if texture:
            textures_loaded += 1
            
            # Create a transformed version to use more memory
            small_resource_manager.get_transformed_texture(
                resource_id, 
                scale=(1.5, 1.5), 
                color=(200, 100, 100)
            )
    
    end_time = time.time()
    scene.load_times.append(end_time - start_time)
    
    # Get cache stats
    scene.stats = small_resource_manager.get_stats()
    
    # Update stats labels
    scene.stats_labels[0].set_text(f"Textures loaded: {textures_loaded}")
    scene.stats_labels[1].set_text(f"Memory usage: {scene.stats['cache']['memory_usage_mb']:.2f}MB / {scene.stats['cache']['max_memory_mb']:.2f}MB")
    scene.stats_labels[2].set_text(f"Resources in cache: {scene.stats['cache']['total_resources']}")
    scene.stats_labels[3].set_text("Some resources were automatically unloaded to stay under the memory limit.")
    
    if len(scene.load_times) > 0:
        scene.stats_labels[4].set_text(f"Load time: {scene.load_times[0]*1000:.2f}ms")
