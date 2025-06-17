import time
import pygame
from engine.core.entity import Entity
from engine.core.components.texture_renderer import TextureRenderer

def run_demo(scene):
    """Demo showing asynchronous preloading"""
    scene.demo_state = "preloading"
    scene.load_times = []
    scene.preload_progress = 0
    scene.preload_total = 10
    
    # Clear cache
    scene.resource_manager.clear_cache()
    
    # Start preloading resources
    base_texture_path = "assets/character.png"
    
    # Define a callback to track progress
    def on_resource_loaded(resource_id):
        scene.preload_progress += 1
        
        # When all resources are loaded, create entities
        if scene.preload_progress >= scene.preload_total:
            create_preloaded_entities(scene)
    
    # Preload the same texture with different IDs
    for i in range(scene.preload_total):
        resource_id = f"preload_texture_{i}"
        scene.resource_manager.preload_resource(base_texture_path, resource_id, "texture")
        scene.resource_manager.on_resource_loaded(resource_id, on_resource_loaded)

def create_preloaded_entities(scene):
    """Create entities using preloaded resources"""
    scene.demo_state = "running"
    
    # Create entities in a grid
    grid_size = 3
    spacing = 100
    start_x = 300
    start_y = 150
    
    for i in range(scene.preload_total):
        resource_id = f"preload_texture_{i}"
        
        row = i // grid_size
        col = i % grid_size
        
        entity = Entity()
        entity.position.x = start_x + col * spacing
        entity.position.y = start_y + row * spacing
        
        texture_renderer = TextureRenderer()
        texture_renderer.load_texture(resource_id)  # Load from cache
        entity.add_component(texture_renderer)
        
        scene.add_entity(entity)
        scene.demo_entities.append(entity)
    
    # Get cache stats
    scene.stats = scene.resource_manager.get_stats()
    
    # Update stats labels
    scene._update_stats_labels()
