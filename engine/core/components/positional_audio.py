import pygame
import math
from ..component import Component
from ..audio_manager import init_audio

class PositionalAudioComponent(Component):
    def __init__(self, audio_path, max_distance=500, min_distance=50, fov=360):
        super().__init__()
        self.audio_path = audio_path
        self.max_distance = max_distance  # Distance at which sound becomes inaudible
        self.min_distance = min_distance  # Distance at which sound is at full volume
        self.fov = math.radians(fov)  # Field of view in radians
        self.position = (0, 0)
        self.listener = None  # Reference to the listener entity
        self.listener_direction = 0  # Angle in radians (0 = right, pi/2 = up)
        
        # Ensure mixer initialized once via audio manager
        init_audio()
            
        # Load and setup the sound
        self.sound = pygame.mixer.Sound(audio_path)
        self.channel = None
        self.is_playing = False
        
    def set_position(self, x, y):
        """Set the position of the audio source"""
        self.position = (x, y)
        
    def set_listener(self, listener_entity):
        """Set the entity that will be used as the audio listener"""
        self.listener = listener_entity
        
    def set_listener_direction(self, angle_degrees):
        """Set the direction the listener is facing (0 = right, 90 = up)"""
        self.listener_direction = math.radians(angle_degrees)
        
    def play(self, loops=-1):
        """Start playing the audio"""
        if not self.is_playing:
            self.channel = self.sound.play(loops=loops)
            self.is_playing = True
            
    def stop(self):
        """Stop playing the audio"""
        if self.is_playing and self.channel:
            self.channel.stop()
            self.is_playing = False
            
    def calculate_audio_properties(self, listener_pos):
        """Calculate volume and panning based on listener position and direction"""
        dx = self.position[0] - listener_pos[0]
        dy = self.position[1] - listener_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Calculate angle between listener and sound source
        angle_to_source = math.atan2(dy, dx)
        
        # Calculate relative angle (considering listener's direction)
        relative_angle = (angle_to_source - self.listener_direction) % (2 * math.pi)
        if relative_angle > math.pi:
            relative_angle -= 2 * math.pi
            
        # Calculate if sound is in field of view
        angle_factor = 1.0
        if abs(relative_angle) > self.fov / 2:
            # Sound is outside FOV, reduce volume
            angle_factor = 0.3
        
        # Calculate base volume from distance
        if distance <= self.min_distance:
            volume = 1.0
        elif distance >= self.max_distance:
            volume = 0.0
        else:
            volume = 1.0 - ((distance - self.min_distance) / (self.max_distance - self.min_distance))
            
        # Apply angle factor to volume
        volume *= angle_factor
        
        # Calculate panning (-1 = left, 1 = right)
        # Use relative angle for panning
        pan = math.sin(relative_angle)
        
        return volume, pan
            
    def update(self):
        """Update the audio based on listener position and direction"""
        if self.is_playing and self.channel and self.entity and self.listener:
            # Get listener position
            listener_pos = (self.listener.position.x, self.listener.position.y)
            
            # Calculate volume and panning
            volume, pan = self.calculate_audio_properties(listener_pos)
            
            # Apply volume
            self.channel.set_volume(volume * (1 - max(0, pan)), volume * (1 + min(0, pan)))
    
    def detach(self):
        """Clean up when component is detached"""
        self.stop()
        super().detach()
