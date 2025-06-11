import pygame
import os
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.sprite_animation import SpriteAnimation

class SpriteAnimationDemo(BaseScene):
    def __init__(self):
        super().__init__()
        self.character = None
        self.sprite_animation = None
        self.current_speed = 1.0
        self.walking_left = False
        self.walking_right = False
        
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
        sprite_sheet_path = "examples/assets/character.png"
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
                
                # Add jump animation (third row: 3 frames of 150x500)
                if self.sprite_animation.create_animation_from_lane(
                    name="jump",
                    start_x=0,          # Start at beginning of third row
                    start_y=320,        # Third row (after 320 pixels)
                    frame_width=150,     # Each frame is 150 pixels wide
                    frame_height=200,    # Each frame is 500 pixels high
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
        
        # Mark scene as loaded
        self._is_loaded = True
        self._loading_progress = 100
        print("Resources loaded")
        
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
                for anim_name in self.sprite_animation.animations:
                    self.sprite_animation.set_animation_speed(anim_name, self.current_speed)
            elif event.key == pygame.K_DOWN:
                self.current_speed = max(0.2, self.current_speed - 0.2)
                print(f"Decreasing animation speed: {self.current_speed:.1f}x")
                for anim_name in self.sprite_animation.animations:
                    self.sprite_animation.set_animation_speed(anim_name, self.current_speed)
        
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT and self.walking_left:
                print("Stopped walking left")
                self.walking_left = False
                self.sprite_animation.play("idle")
            elif event.key == pygame.K_RIGHT and self.walking_right:
                print("Stopped walking right")
                self.walking_right = False
                self.sprite_animation.play("idle")
    
    def update(self):
        """Update the scene"""
        super().update()
        
        # Update character position based on walking state
        if self.walking_left:
            self.character.position.x -= 2
        elif self.walking_right:
            self.character.position.x += 2
    
    def render(self, screen: pygame.Surface):
        """Render the scene"""
        # Fill background
        screen.fill((50, 50, 50))
        
        # Render entities
        super().render(screen)
        
        # Draw instructions
        if pygame.font.get_init():
            font = pygame.font.Font(None, 24)
            instructions = [
                "Press 1: Play Idle Animation (5 frames, 100x160)",
                "Hold Left/Right: Walk Animation (5 frames, 100x160)",
                "Press 3: Play Jump Animation (3 frames, 150x500)",
                "Up/Down Arrows: Change Animation Speed",
                f"Current Speed: {self.current_speed:.1f}x"
            ]
            
            y = 10
            for instruction in instructions:
                text = font.render(instruction, True, (255, 255, 255))
                screen.blit(text, (10, y))
                y += 25
