import time
import pygame
from engine.core.entity import Entity
from engine.core.components.sprite_animation import SpriteAnimation

def run_demo(scene):
    """Demo showing sprite sheet frame caching"""
    scene.demo_state = "running"
    scene.load_times = []
    
    # Load sprite sheet
    sprite_sheet_path = "assets/character_sheet.png"
    
    # First animation - should extract frames and cache them
    entity1 = Entity()
    entity1.position.x = 300
    entity1.position.y = 200
    
    sprite_anim1 = SpriteAnimation()
    
    start_time = time.time()
    sprite_anim1.load_sprite_sheet(sprite_sheet_path)
    sprite_anim1.create_animation_from_lane(
        name="walk",
        start_x=0,
        start_y=0,
        frame_width=64,
        frame_height=64,
        frame_count=8,
        frame_duration=0.1,
        loop=True
    )
    end_time = time.time()
    scene.load_times.append(end_time - start_time)
    
    sprite_anim1.play("walk")
    entity1.add_component(sprite_anim1)
    scene.add_entity(entity1)
    scene.demo_entities.append(entity1)
    
    # Second animation - should use cached frames
    entity2 = Entity()
    entity2.position.x = 500
    entity2.position.y = 200
    
    sprite_anim2 = SpriteAnimation()
    
    start_time = time.time()
    sprite_anim2.load_sprite_sheet(sprite_sheet_path)
    sprite_anim2.create_animation_from_lane(
        name="walk",
        start_x=0,
        start_y=0,
        frame_width=64,
        frame_height=64,
        frame_count=8,
        frame_duration=0.1,
        loop=True
    )
    end_time = time.time()
    scene.load_times.append(end_time - start_time)
    
    sprite_anim2.play("walk")
    entity2.add_component(sprite_anim2)
    scene.add_entity(entity2)
    scene.demo_entities.append(entity2)
    
    # Get cache stats
    scene.stats = scene.resource_manager.get_stats()
    
    # Update stats labels
    scene._update_stats_labels()
