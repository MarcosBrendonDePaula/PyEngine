import pygame
from typing import Dict, List, Optional, Tuple, Callable
from ..component import Component
from ..resource_manager import ResourceManager

class AnimationFrame:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

class Animation:
    def __init__(self, name: str, frames: List[pygame.Surface], frame_duration: float = 0.1, loop: bool = True):
        self.name = name
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop
        self.current_frame = 0
        self.time_accumulated = 0
        self.finished = False
        self.speed_multiplier = 1.0
        self.on_finish_callback: Optional[Callable] = None
        self.on_frame_callback: Optional[Callable[[int], None]] = None
        self.queued_animation: Optional[str] = None
    
    def reset(self):
        self.current_frame = 0
        self.time_accumulated = 0
        self.finished = False

class SpriteAnimation(Component):
    def __init__(self):
        super().__init__()
        self.sprite_sheet: Optional[pygame.Surface] = None
        self.animations: Dict[str, Animation] = {}
        self.current_animation: Optional[Animation] = None
        self.flip_x = False
        self.flip_y = False
        self.scale = (1, 1)
        self.sprite_path: Optional[str] = None
        self.resource_id: Optional[str] = None
        self.resource_manager = ResourceManager.get_instance()
    
    def load_sprite_sheet(self, path: str, colorkey: Optional[Tuple[int, int, int]] = None, resource_id: str = None):
        """
        Load a sprite sheet using the ResourceManager for caching.
        
        Args:
            path: Path to the sprite sheet image
            colorkey: Optional color key for transparency
            resource_id: Optional ID for the resource (defaults to path)
            
        Returns:
            bool: True if loading was successful
        """
        self.resource_id = resource_id or path
        self.sprite_path = path
        
        # Load the sprite sheet using ResourceManager
        self.sprite_sheet = self.resource_manager.load_texture(path, self.resource_id, colorkey)
        
        if self.sprite_sheet:
            print(f"Loaded sprite sheet: {path}")
            return True
        else:
            print(f"Could not load sprite sheet {path}")
            return False
    
    def extract_frames_from_lane(self, start_x: int, start_y: int, frame_width: int, frame_height: int, 
                               frame_count: int, lane_width: Optional[int] = None) -> List[pygame.Surface]:
        """
        Extract frames from a specific lane in the sprite sheet using ResourceManager for caching.
        
        Args:
            start_x: Starting X position of the lane
            start_y: Starting Y position of the lane
            frame_width: Width of each frame
            frame_height: Height of each frame
            frame_count: Number of frames to extract
            lane_width: Optional width limit for the lane (to prevent overflow into next animation)
            
        Returns:
            List of frame surfaces
        """
        if not self.sprite_sheet or not self.resource_id:
            return []
        
        # Use ResourceManager to extract and cache frames
        sheet_width = self.sprite_sheet.get_width()
        max_x = sheet_width if lane_width is None else start_x + lane_width
        actual_frame_count = frame_count
        
        # Calculate actual frame count based on lane width
        for i in range(frame_count):
            x = start_x + (i * frame_width)
            if x + frame_width > max_x:
                actual_frame_count = i
                break
        
        # Use ResourceManager to extract and cache frames with transformations
        return self.resource_manager.extract_sprite_frames(
            self.resource_id,
            start_x,
            start_y,
            frame_width,
            frame_height,
            actual_frame_count or frame_count,
            scale=self.scale if self.scale != (1, 1) else None,
            flip=(self.flip_x, self.flip_y) if (self.flip_x or self.flip_y) else None
        )
    
    def create_animation_from_lane(self, name: str, start_x: int, start_y: int, 
                                 frame_width: int, frame_height: int, frame_count: int,
                                 frame_duration: float = 0.1, loop: bool = True,
                                 lane_width: Optional[int] = None) -> bool:
        """
        Create an animation from a specific lane in the sprite sheet
        
        Args:
            name: Name of the animation
            start_x: Starting X position of the lane
            start_y: Starting Y position of the lane
            frame_width: Width of each frame
            frame_height: Height of each frame
            frame_count: Number of frames to extract
            frame_duration: Duration of each frame in seconds
            loop: Whether the animation should loop
            lane_width: Optional width limit for the lane
            
        Returns:
            bool: True if animation was created successfully
        """
        if not self.sprite_sheet:
            print(f"No sprite sheet loaded for animation {name}")
            return False
        
        frames = self.extract_frames_from_lane(
            start_x, start_y, frame_width, frame_height, frame_count, lane_width
        )
        
        if not frames:
            print(f"Failed to extract frames for animation {name}")
            return False
        
        # Create animation
        animation = Animation(name, frames, frame_duration, loop)
        
        # Store original parameters for recreating the animation when scale/flip changes
        animation.original_params = {
            'start_x': start_x,
            'start_y': start_y,
            'frame_width': frame_width,
            'frame_height': frame_height,
            'frame_count': frame_count
        }
        
        if lane_width is not None:
            animation.original_params['lane_width'] = lane_width
            
        self.animations[name] = animation
        print(f"Created animation '{name}' with {len(frames)} frames")
        return True
    
    def set_animation_speed(self, animation_name: str, speed_multiplier: float):
        """Set the speed multiplier for an animation"""
        if animation_name in self.animations:
            self.animations[animation_name].speed_multiplier = speed_multiplier
    
    def queue_animation(self, animation_name: str):
        """Queue an animation to play after the current one finishes"""
        if self.current_animation and animation_name in self.animations:
            self.current_animation.queued_animation = animation_name
    
    def set_animation_callback(self, animation_name: str, on_finish: Optional[Callable] = None, 
                             on_frame: Optional[Callable[[int], None]] = None):
        """Set callbacks for animation events"""
        if animation_name in self.animations:
            animation = self.animations[animation_name]
            animation.on_finish_callback = on_finish
            animation.on_frame_callback = on_frame
    
    def play(self, animation_name: str, reset: bool = True) -> bool:
        """Play the specified animation"""
        if animation_name not in self.animations:
            print(f"Animation '{animation_name}' not found!")
            return False
        
        if self.current_animation and self.current_animation.name == animation_name and not reset:
            return True
        
        self.current_animation = self.animations[animation_name]
        if reset:
            self.current_animation.reset()
        print(f"Playing animation: {animation_name}")
        return True
    
    def stop(self):
        """Stop the current animation"""
        self.current_animation = None
    
    def set_scale(self, scale_x: float, scale_y: float):
        """Set the scale of the sprite animations"""
        if self.scale == (scale_x, scale_y):
            return
        
        self.scale = (scale_x, scale_y)
        
        # Recreate all animations with new scale
        if self.sprite_sheet and self.animations and self.resource_id:
            current_anim = self.current_animation.name if self.current_animation else None
            
            # Store animation properties to recreate them
            animations_to_recreate = []
            for name, anim in self.animations.items():
                # Find the original animation parameters
                if hasattr(anim, 'original_params'):
                    animations_to_recreate.append((name, anim.original_params, anim.frame_duration, anim.loop))
                else:
                    # Fallback for animations without original params
                    frames = [pygame.transform.scale(
                        frame,
                        (int(frame.get_width() * scale_x), int(frame.get_height() * scale_y))
                    ) for frame in anim.frames]
                    new_anim = Animation(name, frames, anim.frame_duration, anim.loop)
                    self.animations[name] = new_anim
            
            # Clear animations that will be recreated
            for name, _, _, _ in animations_to_recreate:
                if name in self.animations:
                    del self.animations[name]
            
            # Recreate animations with new scale
            for name, params, duration, loop in animations_to_recreate:
                self.create_animation_from_lane(
                    name=name,
                    start_x=params['start_x'],
                    start_y=params['start_y'],
                    frame_width=params['frame_width'],
                    frame_height=params['frame_height'],
                    frame_count=params['frame_count'],
                    frame_duration=duration,
                    loop=loop,
                    lane_width=params.get('lane_width')
                )
            
            if current_anim and current_anim in self.animations:
                self.play(current_anim)
    
    def set_flip(self, flip_x: bool, flip_y: bool):
        """Set the flip state of the sprite"""
        if self.flip_x == flip_x and self.flip_y == flip_y:
            return
        
        self.flip_x = flip_x
        self.flip_y = flip_y
        
        # Recreate all animations with new flip state
        if self.sprite_sheet and self.animations and self.resource_id:
            current_anim = self.current_animation.name if self.current_animation else None
            
            # Store animation properties to recreate them
            animations_to_recreate = []
            for name, anim in self.animations.items():
                # Find the original animation parameters
                if hasattr(anim, 'original_params'):
                    animations_to_recreate.append((name, anim.original_params, anim.frame_duration, anim.loop))
                else:
                    # Fallback for animations without original params
                    frames = [pygame.transform.flip(frame, flip_x, flip_y) for frame in anim.frames]
                    new_anim = Animation(name, frames, anim.frame_duration, anim.loop)
                    self.animations[name] = new_anim
            
            # Clear animations that will be recreated
            for name, _, _, _ in animations_to_recreate:
                if name in self.animations:
                    del self.animations[name]
            
            # Recreate animations with new flip state
            for name, params, duration, loop in animations_to_recreate:
                self.create_animation_from_lane(
                    name=name,
                    start_x=params['start_x'],
                    start_y=params['start_y'],
                    frame_width=params['frame_width'],
                    frame_height=params['frame_height'],
                    frame_count=params['frame_count'],
                    frame_duration=duration,
                    loop=loop,
                    lane_width=params.get('lane_width')
                )
            
            if current_anim and current_anim in self.animations:
                self.play(current_anim)
    
    def tick(self):
        """Update the animation state - called every frame"""
        if not self.current_animation:
            return
        
        if self.current_animation.finished:
            if self.current_animation.queued_animation:
                next_animation = self.current_animation.queued_animation
                self.current_animation.queued_animation = None
                self.play(next_animation)
            if self.current_animation.on_finish_callback:
                self.current_animation.on_finish_callback()
            return
        
        # Update frame based on time and speed multiplier
        frame_duration = self.current_animation.frame_duration / self.current_animation.speed_multiplier
        dt = 1/60
        if self.entity and self.entity.scene and self.entity.scene.interface:
            dt = self.entity.scene.interface.clock.get_time() / 1000.0
        self.current_animation.time_accumulated += dt
        
        while self.current_animation.time_accumulated >= frame_duration:
            self.current_animation.time_accumulated -= frame_duration
            prev_frame = self.current_animation.current_frame
            self.current_animation.current_frame += 1
            
            if (self.current_animation.on_frame_callback and 
                prev_frame != self.current_animation.current_frame):
                self.current_animation.on_frame_callback(self.current_animation.current_frame)
            
            if self.current_animation.current_frame >= len(self.current_animation.frames):
                if self.current_animation.loop:
                    self.current_animation.current_frame = 0
                else:
                    self.current_animation.current_frame = len(self.current_animation.frames) - 1
                    self.current_animation.finished = True
    
    def render(self, screen: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)):
        """Render the current animation frame"""
        if not self.enabled or not self.current_animation or not self.entity:
            return
        
        current_frame = self.current_animation.frames[self.current_animation.current_frame]
        
        render_pos = (
            self.entity.position.x - camera_offset[0] - current_frame.get_width() / 2,
            self.entity.position.y - camera_offset[1] - current_frame.get_height() / 2
        )
        
        screen.blit(current_frame, render_pos)
