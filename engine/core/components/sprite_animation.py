import pygame
from typing import Dict, List, Optional, Tuple, Callable
from ..component import Component

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
    
    def load_sprite_sheet(self, path: str, colorkey: Optional[Tuple[int, int, int]] = None):
        try:
            self.sprite_sheet = pygame.image.load(path).convert_alpha()
            if colorkey is not None:
                self.sprite_sheet.set_colorkey(colorkey)
            
            self.sprite_path = path
            print(f"Loaded sprite sheet: {path}")
            return True
        except pygame.error as e:
            print(f"Could not load sprite sheet {path}: {e}")
            return False
    
    def extract_frames_from_lane(self, start_x: int, start_y: int, frame_width: int, frame_height: int, 
                               frame_count: int, lane_width: Optional[int] = None) -> List[pygame.Surface]:
        """
        Extract frames from a specific lane in the sprite sheet
        
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
        if not self.sprite_sheet:
            return []
        
        frames = []
        sheet_width = self.sprite_sheet.get_width()
        max_x = sheet_width if lane_width is None else start_x + lane_width
        
        for i in range(frame_count):
            x = start_x + (i * frame_width)
            if x + frame_width > max_x:
                break
                
            # Create frame surface
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            
            # Extract frame from sprite sheet
            frame.blit(self.sprite_sheet, (0, 0), (x, start_y, frame_width, frame_height))
            
            # Apply scale if needed
            if self.scale != (1, 1):
                scaled_width = int(frame_width * self.scale[0])
                scaled_height = int(frame_height * self.scale[1])
                frame = pygame.transform.scale(frame, (scaled_width, scaled_height))
            
            # Apply flip if needed
            if self.flip_x or self.flip_y:
                frame = pygame.transform.flip(frame, self.flip_x, self.flip_y)
            
            frames.append(frame)
        
        return frames
    
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
        self.animations[name] = Animation(name, frames, frame_duration, loop)
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
        if self.sprite_sheet and self.animations:
            current_anim = self.current_animation.name if self.current_animation else None
            animations_to_recreate = list(self.animations.items())
            self.animations.clear()
            
            for name, anim in animations_to_recreate:
                frames = [pygame.transform.scale(
                    frame,
                    (int(frame.get_width() * scale_x), int(frame.get_height() * scale_y))
                ) for frame in anim.frames]
                self.animations[name] = Animation(name, frames, anim.frame_duration, anim.loop)
            
            if current_anim:
                self.play(current_anim)
    
    def set_flip(self, flip_x: bool, flip_y: bool):
        """Set the flip state of the sprite"""
        if self.flip_x == flip_x and self.flip_y == flip_y:
            return
        
        self.flip_x = flip_x
        self.flip_y = flip_y
        
        # Recreate all animations with new flip state
        if self.sprite_sheet and self.animations:
            current_anim = self.current_animation.name if self.current_animation else None
            animations_to_recreate = list(self.animations.items())
            self.animations.clear()
            
            for name, anim in animations_to_recreate:
                frames = [pygame.transform.flip(frame, flip_x, flip_y) for frame in anim.frames]
                self.animations[name] = Animation(name, frames, anim.frame_duration, anim.loop)
            
            if current_anim:
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
        self.current_animation.time_accumulated += 1/60  # Assuming 60 FPS
        
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
