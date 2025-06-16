import pygame
import os
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.sprite_animation import SpriteAnimation
from engine.core.components.ui.label import Label

class SpriteAnimationDemo(BaseScene):
    def __init__(self):
        super().__init__()
        self.character = None
        self.sprite_animation = None
        self.current_speed = 1.0
        self.walking_left = False
        self.walking_right = False
        self.instruction_labels = []
        self.speed_label = None
        
    def on_animation_finish(self):
        """Callback when an animation finishes"""
        print("Animation finished!")
        
    def on_frame_change(self, frame_number: int):
        """Callback when animation frame changes"""
        print(f"Frame changed to: {frame_number}")
        
    def load_resources(self):
        """Load all required resources"""
        print("Loading resources for SpriteAnimationDemo")
        
        # Create character entity
        self.character = Entity()
        self.sprite_animation = SpriteAnimation()
        self.character.add_component(self.sprite_animation)
        self.character.position = pygame.math.Vector2(400, 300)  # Center of screen
        
        # Load sprite sheet and extract frames
        sprite_sheet_path = "assets/character.png"
        if os.path.exists(sprite_sheet_path):
            print("Loading sprite sheet")
            # Load the sprite sheet (500x500 pixels)
            if self.sprite_animation.load_sprite_sheet(sprite_sheet_path):
                # Add idle animation (first row: 5 frames of 100x160)
                if self.sprite_animation.create_animation_from_lane(
                    name="idle",
                    start_x=0,          # Start at beginning of first row
                    start_y=0,          # First row
                    frame_width=100,     # Each frame is 100 pixels wide
                    frame_height=160,    # Each frame is 160 pixels high
                    frame_count=5,       # 5 frames in this animation
                    frame_duration=0.2,
                    loop=True
                ):
                    print("Added idle animation")
                    self.sprite_animation.set_animation_callback(
                        "idle",
                        on_finish=self.on_animation_finish,
                        on_frame=self.on_frame_change
                    )
                
                # Add walk animation (second row: 5 frames of 100x160)
                if self.sprite_animation.create_animation_from_lane(
                    name="walk",
                    start_x=0,          # Start at beginning of second row
                    start_y=160,        # Second row (after 160 pixels)
                    frame_width=100,     # Each frame is 100 pixels wide
                    frame_height=160,    # Each frame is 160 pixels high
                    frame_count=5,       # 5 frames in this animation
                    frame_duration=0.15,
                    loop=True
                ):
                    print("Added walk animation")
                
                # Add jump animation (third row: 3 frames of 150x200)
                # Fixed the frame_height from 500 to 200 to match the comment
                if self.sprite_animation.create_animation_from_lane(
                    name="jump",
                    start_x=0,          # Start at beginning of third row
                    start_y=320,        # Third row (after 320 pixels)
                    frame_width=150,     # Each frame is 150 pixels wide
                    frame_height=200,    # Each frame is 200 pixels high
                    frame_count=3,       # 3 frames in this animation
                    frame_duration=0.2,
                    loop=True
                ):
                    print("Added jump animation")
                
                # Start with idle animation
                if self.sprite_animation.play("idle"):
                    print("Started idle animation")
                    
                # Add character to scene
                self.add_entity(self.character)
        else:
            print(f"Error: Sprite sheet not found at {sprite_sheet_path}")
            # Create a fallback colored rectangle for testing
            self._create_fallback_character()
        
        # Create instruction labels
        self._create_instruction_labels()
        
        # Mark scene as loaded
        self._is_loaded = True
        self._loading_progress = 100
        print("Resources loaded")
    
    def _create_fallback_character(self):
        """Create a simple colored rectangle as fallback when sprite sheet is missing"""
        print("Creating fallback character")
        # Even without sprite sheet, we can still demonstrate the animation system
        self.character = Entity()
        self.character.position = pygame.math.Vector2(400, 300)
        self.add_entity(self.character)
    
    def _create_instruction_labels(self):
        """Create instruction labels using the engine's label system"""
        instructions = [
            "Press 1: Play Idle Animation (5 frames, 100x160)",
            "Hold Left/Right: Walk Animation (5 frames, 100x160)",
            "Press 3: Play Jump Animation (3 frames, 150x200)",
            "Up/Down Arrows: Change Animation Speed"
        ]
        
        # Clear existing labels
        for label in self.instruction_labels:
            self.add_entity(label)
        self.instruction_labels.clear()
        
        # Remove existing speed label
        if self.speed_label:
            self.add_entity(self.speed_label)
        
        # Create instruction labels and add to scene
        y_offset = 10
        for instruction in instructions:
            label = Label(
                x=10,
                y=y_offset,
                text=instruction,
                font_size=20
            )
            label.set_text_color((255, 255, 255))  # White text
            self.instruction_labels.append(label)
            self.add_entity(label)  # Add to scene
            y_offset += 25
        
        # Create speed label and add to scene
        self.speed_label = Label(
            x=10,
            y=y_offset,
            text=f"Current Speed: {self.current_speed:.1f}x",
            font_size=20
        )
        self.speed_label.set_text_color((255, 255, 0))  # Yellow for emphasis
        self.add_entity(self.speed_label)  # Add to scene
        
    def _update_speed_display(self):
        """Update the speed display label"""
        if self.speed_label:
            self.speed_label.set_text(f"Current Speed: {self.current_speed:.1f}x")
        
    def handle_event(self, event: pygame.event.Event):
        """Handle input to change animations"""
        super().handle_event(event)
        
        if not self.sprite_animation:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                print("Playing idle animation")
                self.sprite_animation.play("idle")
            elif event.key == pygame.K_3:
                print("Playing jump animation")
                self.sprite_animation.play("jump")
            elif event.key == pygame.K_LEFT:
                print("Walking left")
                self.walking_left = True
                self.walking_right = False
                self.sprite_animation.set_flip(False, False)  # No flip for left
                self.sprite_animation.play("walk")
            elif event.key == pygame.K_RIGHT:
                print("Walking right")
                self.walking_right = True
                self.walking_left = False
                self.sprite_animation.set_flip(True, False)  # Flip for right
                self.sprite_animation.play("walk")
            elif event.key == pygame.K_UP:
                self.current_speed = min(2.0, self.current_speed + 0.2)
                print(f"Increasing animation speed: {self.current_speed:.1f}x")
                if hasattr(self.sprite_animation, 'animations'):
                    for anim_name in self.sprite_animation.animations:
                        self.sprite_animation.set_animation_speed(anim_name, self.current_speed)
                self._update_speed_display()
            elif event.key == pygame.K_DOWN:
                self.current_speed = max(0.2, self.current_speed - 0.2)
                print(f"Decreasing animation speed: {self.current_speed:.1f}x")
                if hasattr(self.sprite_animation, 'animations'):
                    for anim_name in self.sprite_animation.animations:
                        self.sprite_animation.set_animation_speed(anim_name, self.current_speed)
                self._update_speed_display()
        
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT and self.walking_left:
                print("Stopped walking left")
                self.walking_left = False
                if self.sprite_animation:
                    self.sprite_animation.play("idle")
            elif event.key == pygame.K_RIGHT and self.walking_right:
                print("Stopped walking right")
                self.walking_right = False
                if self.sprite_animation:
                    self.sprite_animation.play("idle")
    
    def update(self, delta):
        """Update the scene"""
        super().update(delta)
        
        # Update character position based on walking state
        if self.character and (self.walking_left or self.walking_right):
            if self.walking_left:
                self.character.position.x -= 100 * delta  # Speed based on delta time
            elif self.walking_right:
                self.character.position.x += 100 * delta  # Speed based on delta time
            
            # Keep character on screen
            screen_width = 800  # Assuming screen width, adjust as needed
            if self.character.position.x < 0:
                self.character.position.x = 0
            elif self.character.position.x > screen_width:
                self.character.position.x = screen_width
    
    def render(self, screen: pygame.Surface):
        """Render the scene"""
        # Render entities and UI elements
        super().render(screen)