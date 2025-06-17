import time
import pygame
from engine.core.entity import Entity
from engine.core.components.texture_renderer import TextureRenderer

def run_demo(scene):
    """Demo showing transformation caching"""
    scene.demo_state = "running"
    scene.load_times = []
    
    texture_path = "assets/character.png"
    
    # Original texture
    entity1 = Entity()
    entity1.position.x = 250
    entity1.position.y = 200
    
    texture_renderer1 = TextureRenderer()
    texture_renderer1.load_texture(texture_path)
    entity1.add_component(texture_renderer1)
    scene.add_entity(entity1)
    scene.demo_entities.append(entity1)
    
    # Scaled texture - first time (not cached)
    entity2 = Entity()
    entity2.position.x = 400
    entity2.position.y = 200
    
    texture_renderer2 = TextureRenderer()
    texture_renderer2.load_texture(texture_path)
    
    start_time = time.time()
    texture_renderer2.set_scale(2.0, 2.0)
    # Force rendering to create the transformed texture
    surface = pygame.Surface((1, 1))
    texture_renderer2.render(surface, (0, 0))
    end_time = time.time()
    scene.load_times.append(end_time - start_time)
    
    entity2.add_component(texture_renderer2)
    scene.add_entity(entity2)
    scene.demo_entities.append(entity2)
    
    # Scaled texture - second time (should be cached)
    entity3 = Entity()
    entity3.position.x = 550
    entity3.position.y = 200
    
    texture_renderer3 = TextureRenderer()
    texture_renderer3.load_texture(texture_path)
    
    start_time = time.time()
    texture_renderer3.set_scale(2.0, 2.0)
    # Force rendering to create the transformed texture
    surface = pygame.Surface((1, 1))
    texture_renderer3.render(surface, (0, 0))
    end_time = time.time()
    scene.load_times.append(end_time - start_time)
    
    entity3.add_component(texture_renderer3)
    scene.add_entity(entity3)
    scene.demo_entities.append(entity3)
    
    # Get cache stats
    scene.stats = scene.resource_manager.get_stats()
    
    # Update stats labels
    scene._update_stats_labels()
