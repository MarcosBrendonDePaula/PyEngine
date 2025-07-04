"""
Threading Demo Scene - Demonstrates parallel entity updates
"""

import pygame
import random
import time
from engine import BaseScene, Entity, Component

class MovementComponent(Component):
    """Component that moves entities in random directions with physics."""
    
    def __init__(self, speed: float = 100.0):
        super().__init__()
        self.speed = speed
        self.direction_x = random.uniform(-1, 1)
        self.direction_y = random.uniform(-1, 1)
        self.bounce_timer = 0.0
        self.color_timer = 0.0
        
    def update(self):
        if not self.entity:
            return
            
        dt = self.entity.delta_time
        
        # Update position based on velocity
        self.entity.position.x += self.direction_x * self.speed * dt
        self.entity.position.y += self.direction_y * self.speed * dt
        
        # Bounce off screen edges
        if self.entity.position.x < 0 or self.entity.position.x > 800:
            self.direction_x *= -1
        if self.entity.position.y < 0 or self.entity.position.y > 600:
            self.direction_y *= -1
            
        # Keep within bounds
        self.entity.position.x = max(0, min(800, self.entity.position.x))
        self.entity.position.y = max(0, min(600, self.entity.position.y))
        
        # Occasionally change direction (every 2 seconds)
        self.bounce_timer += dt
        if self.bounce_timer > 2.0:
            self.direction_x += random.uniform(-0.5, 0.5)
            self.direction_y += random.uniform(-0.5, 0.5)
            # Normalize direction vector
            length = (self.direction_x**2 + self.direction_y**2)**0.5
            if length > 0:
                self.direction_x /= length
                self.direction_y /= length
            self.bounce_timer = 0.0

class RenderComponent(Component):
    """Component for rendering entities as colored circles."""
    
    def __init__(self, color: tuple = (255, 255, 255), size: int = 5):
        super().__init__()
        self.color = color
        self.size = size
        self.pulse_timer = 0.0
        self.base_size = size
        
    def update(self):
        """Update visual effects."""
        if not self.entity:
            return
            
        # Pulse effect
        self.pulse_timer += self.entity.delta_time * 2
        pulse = 1.0 + 0.2 * abs(math.sin(self.pulse_timer))
        self.size = int(self.base_size * pulse)
        
    def render(self, screen, camera_offset=(0, 0)):
        if not self.entity:
            return
            
        pos = (
            int(self.entity.position.x - camera_offset[0]), 
            int(self.entity.position.y - camera_offset[1])
        )
        pygame.draw.circle(screen, self.color, pos, self.size)

class ThreadingDemoScene(BaseScene):
    """Scene that demonstrates threaded entity updates with performance monitoring."""
    
    def __init__(self, entity_count: int = 1000):
        super().__init__()
        self.entity_count = entity_count
        
        # Performance tracking
        self.frame_times = []
        self.update_times = []
        self.max_samples = 60  # Track last 60 frames
        
        # UI elements
        self.font = None
        self.start_time = None
        
    def on_initialize(self):
        """Initialize the scene with entities and UI."""
        # Initialize pygame font
        pygame.font.init()
        self.font = pygame.font.Font(None, 32)
        self.start_time = time.time()
        
        print(f"Creating {self.entity_count} entities for threading demo...")
        creation_start = time.time()
        
        # Create entities with random properties
        for i in range(self.entity_count):
            # Random starting position
            x = random.uniform(50, 750)
            y = random.uniform(50, 550)
            entity = Entity(x, y)
            
            # Add movement component with random speed
            speed = random.uniform(50, 200)
            movement = MovementComponent(speed)
            entity.add_component(movement)
            
            # Add render component with random color and size
            color = (
                random.randint(100, 255),
                random.randint(100, 255),
                random.randint(100, 255)
            )
            size = random.randint(2, 8)
            renderer = RenderComponent(color, size)
            entity.add_component(renderer)
            
            self.add_entity(entity)
            
        creation_time = time.time() - creation_start
        print(f"✓ Created {self.entity_count} entities in {creation_time:.3f}s")
        
        # Print threading info
        if hasattr(self, '_thread_config'):
            threading_status = "Enabled" if self._thread_config.enabled else "Disabled"
            print(f"✓ Threading: {threading_status}")
            if self._thread_pool and hasattr(self._thread_pool, 'max_workers'):
                print(f"✓ Thread pool: {self._thread_pool.max_workers} workers")
        
    def update(self, delta_time: float):
        """Update scene with performance tracking."""
        update_start = time.time()
        
        # Call parent update (handles entity updates with threading)
        super().update(delta_time)
        
        update_time = time.time() - update_start
        
        # Track performance metrics
        self.update_times.append(update_time)
        if len(self.update_times) > self.max_samples:
            self.update_times.pop(0)
            
    def render(self, screen: pygame.Surface):
        """Render scene with performance overlay."""
        # Fill background
        screen.fill((20, 20, 30))  # Dark blue background
        
        # Render all entities
        super().render(screen)
        
        # Render performance info
        self._render_performance_info(screen)
        
    def _render_performance_info(self, screen: pygame.Surface):
        """Render performance statistics overlay."""
        if not self.font or not self.update_times:
            return
            
        # Calculate metrics
        avg_update_time = sum(self.update_times) / len(self.update_times)
        min_update_time = min(self.update_times)
        max_update_time = max(self.update_times)
        estimated_fps = 1.0 / avg_update_time if avg_update_time > 0 else 0
        
        # Prepare info strings
        info_lines = [
            f"Entities: {len(self.entities)}",
            f"Update: {avg_update_time*1000:.2f}ms (min: {min_update_time*1000:.1f}, max: {max_update_time*1000:.1f})",
            f"Est. FPS: {estimated_fps:.1f}",
        ]
        
        # Add threading info
        if hasattr(self, '_thread_config'):
            threading_status = "ON" if self._thread_config.enabled else "OFF"
            info_lines.append(f"Threading: {threading_status}")
            
            if self._thread_pool and hasattr(self._thread_pool, 'max_workers'):
                info_lines.append(f"Workers: {self._thread_pool.max_workers}")
                
        # Add runtime
        if self.start_time:
            runtime = time.time() - self.start_time
            info_lines.append(f"Runtime: {runtime:.1f}s")
            
        # Render text
        y_offset = 10
        for line in info_lines:
            text_surface = self.font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (10, y_offset))
            y_offset += 35
            
        # Render instructions
        instructions = [
            "ESC - Exit",
            "Watch the performance metrics above"
        ]
        
        y_offset = screen.get_height() - len(instructions) * 25 - 10
        for instruction in instructions:
            text_surface = self.font.render(instruction, True, (200, 200, 200))
            screen.blit(text_surface, (10, y_offset))
            y_offset += 25

# Import math for pulse effect
import math