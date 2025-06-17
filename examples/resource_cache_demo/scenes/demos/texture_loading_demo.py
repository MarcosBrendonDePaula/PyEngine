import time
import pygame
from engine.core.entity import Entity
from engine.core.components.texture_renderer import TextureRenderer

def run_demo(scene):
    """Demo showing texture loading cache"""
    scene.demo_state = "running"
    scene.load_times = []
    
    # First load - should be slow
    start_time = time.time()
    texture_path = "assets/character.png"
    texture = scene.resource_manager.load_texture(texture_path)
    end_time = time.time()
    scene.load_times.append(end_time - start_time)
    
    # Create entity to display the texture
    entity = Entity()
    entity.position.x = 400
    entity.position.y = 200
    
    texture_renderer = TextureRenderer()
    texture_renderer.load_texture(texture_path)
    entity.add_component(texture_renderer)
    
    scene.add_entity(entity)
    scene.demo_entities.append(entity)
    
    # Second load - should be fast (cached)
    start_time = time.time()
    texture2 = scene.resource_manager.load_texture(texture_path)
    end_time = time.time()
    scene.load_times.append(end_time - start_time)
    
    # Create second entity with same texture
    entity2 = Entity()
    entity2.position.x = 500
    entity2.position.y = 200
    
    texture_renderer2 = TextureRenderer()
    texture_renderer2.load_texture(texture_path)
    entity2.add_component(texture_renderer2)
    
    scene.add_entity(entity2)
    scene.demo_entities.append(entity2)
    
    # Get cache stats
    scene.stats = scene.resource_manager.get_stats()
    
    # Update stats labels
    scene._update_stats_labels()
