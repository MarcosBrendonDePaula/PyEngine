"""
Threading Demo Scene - Demonstrates parallel entity updates
Creates many entities with physics and visual effects to showcase threading performance
"""

import pygame
import random
import time
import math
from engine import BaseScene, Entity, Component, ThreadConfig

class MovementComponent(Component):
    """Component that moves entities in random directions with realistic physics."""
    
    def __init__(self, speed: float = 100.0):
        super().__init__()
        self.speed = speed
        self.direction_x = random.uniform(-1, 1)
        self.direction_y = random.uniform(-1, 1)
        self.bounce_timer = 0.0
        self.bounce_cooldown = random.uniform(1.5, 3.0)  # Random direction change interval
        
    def update(self):
        if not self.entity:
            return
            
        dt = self.entity.delta_time
        
        # Update position based on velocity
        self.entity.position.x += self.direction_x * self.speed * dt
        self.entity.position.y += self.direction_y * self.speed * dt
        
        # Bounce off screen edges with slight randomness
        if self.entity.position.x < 0 or self.entity.position.x > 800:
            self.direction_x *= -1
            self.direction_x += random.uniform(-0.1, 0.1)  # Add slight randomness
        if self.entity.position.y < 0 or self.entity.position.y > 600:
            self.direction_y *= -1
            self.direction_y += random.uniform(-0.1, 0.1)  # Add slight randomness
            
        # Keep within bounds
        self.entity.position.x = max(0, min(800, self.entity.position.x))
        self.entity.position.y = max(0, min(600, self.entity.position.y))
        
        # Occasionally change direction
        self.bounce_timer += dt
        if self.bounce_timer > self.bounce_cooldown:
            self.direction_x += random.uniform(-0.5, 0.5)
            self.direction_y += random.uniform(-0.5, 0.5)
            # Normalize direction vector
            length = (self.direction_x**2 + self.direction_y**2)**0.5
            if length > 0:
                self.direction_x /= length
                self.direction_y /= length
            self.bounce_timer = 0.0
            self.bounce_cooldown = random.uniform(1.5, 3.0)  # New random interval

class RenderComponent(Component):
    """Component for rendering entities with visual effects."""
    
    def __init__(self, color: tuple = (255, 255, 255), size: int = 5):
        super().__init__()
        self.base_color = color
        self.color = color
        self.size = size
        self.base_size = size
        self.pulse_timer = 0.0
        self.pulse_speed = random.uniform(1.0, 3.0)
        
    def update(self):
        """Update visual effects like pulsing and color variation."""
        if not self.entity:
            return
            
        dt = self.entity.delta_time
        self.pulse_timer += dt * self.pulse_speed
        
        # Pulse effect for size
        pulse = 1.0 + 0.3 * math.sin(self.pulse_timer)
        self.size = max(1, int(self.base_size * pulse))
        
        # Subtle color variation
        color_variation = 0.1 * math.sin(self.pulse_timer * 0.5)
        self.color = (
            max(0, min(255, int(self.base_color[0] * (1 + color_variation)))),
            max(0, min(255, int(self.base_color[1] * (1 + color_variation)))),
            max(0, min(255, int(self.base_color[2] * (1 + color_variation))))
        )
        
    def render(self, screen, camera_offset=(0, 0)):
        if not self.entity:
            return
            
        pos = (
            int(self.entity.position.x - camera_offset[0]), 
            int(self.entity.position.y - camera_offset[1])
        )
        pygame.draw.circle(screen, self.color, pos, self.size)
        
        # Add a subtle glow effect for larger entities
        if self.size > 5:
            glow_color = tuple(c // 3 for c in self.color)
            pygame.draw.circle(screen, glow_color, pos, self.size + 2, 1)

class ThreadingDemoScene(BaseScene):
    """Scene that demonstrates threaded entity updates with comprehensive performance monitoring."""
    
    def __init__(self, entity_count: int = 1000, threading_enabled: bool = True):
        # Configure threading with optimized settings
        thread_config = ThreadConfig(
            enabled=threading_enabled,
            max_workers=None,  # Auto-detect optimal worker count
            min_entities_for_threading=50,  # Start threading with 50+ entities
            batch_size_multiplier=1.5,  # Optimal batch size multiplier
            use_global_pool=True  # Use shared thread pool for efficiency
        )
        
        super().__init__(thread_config=thread_config)
        self.entity_count = entity_count
        self.threading_enabled = threading_enabled
        
        # Performance tracking
        self.frame_times = []
        self.update_times = []
        self.render_times = []
        self.max_samples = 60  # Track last 60 frames
        
        # UI and timing
        self.font = None
        self.small_font = None
        self.start_time = None
        
    def on_initialize(self):
        """Create entities and initialize the demo scene."""
        # Initialize pygame font system
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.start_time = time.time()
        
        print(f"Creating {self.entity_count} entities for threading demo...")
        creation_start = time.time()
        
        # Create entities with varied properties for interesting visuals
        for i in range(self.entity_count):
            # Random starting position (avoid edges)
            x = random.uniform(50, 750)
            y = random.uniform(50, 550)
            entity = Entity(x, y)
            
            # Add movement component with varied speeds
            speed = random.uniform(50, 250)
            movement = MovementComponent(speed)
            entity.add_component(movement)
            
            # Add render component with varied colors and sizes
            # Create more interesting color palettes
            color_type = random.choice(['warm', 'cool', 'bright'])
            if color_type == 'warm':
                color = (random.randint(150, 255), random.randint(100, 200), random.randint(50, 150))
            elif color_type == 'cool':
                color = (random.randint(50, 150), random.randint(100, 200), random.randint(150, 255))
            else:  # bright
                color = (random.randint(200, 255), random.randint(200, 255), random.randint(100, 255))
                
            size = random.randint(2, 10)
            renderer = RenderComponent(color, size)
            entity.add_component(renderer)
            
            self.add_entity(entity)
            
        creation_time = time.time() - creation_start
        print(f"✓ Created {self.entity_count} entities in {creation_time:.3f}s")
        
        # Display threading configuration
        threading_status = "Enabled" if self.threading_enabled else "Disabled"
        print(f"✓ Threading: {threading_status}")
        
        if hasattr(self, '_thread_pool') and self._thread_pool:
            print(f"✓ Thread pool: {self._thread_pool.max_workers} workers")
            print(f"✓ Min entities for threading: {self._thread_config.min_entities_for_threading}")
        
        print(f"✓ Scene initialized successfully")
        
    def update(self, delta_time: float):
        """Update scene with detailed performance tracking."""
        update_start = time.time()
        
        # Call parent update (handles entity updates with threading)
        super().update(delta_time)
        
        update_time = time.time() - update_start
        
        # Track performance metrics
        self.update_times.append(update_time)
        if len(self.update_times) > self.max_samples:
            self.update_times.pop(0)
            
    def render(self, screen: pygame.Surface):
        """Render scene with comprehensive performance overlay."""
        render_start = time.time()
        
        # Clear screen with gradient-like background
        screen.fill((10, 15, 25))  # Dark background for better contrast
        
        # Render all entities
        super().render(screen)
        
        render_time = time.time() - render_start
        self.render_times.append(render_time)
        if len(self.render_times) > self.max_samples:
            self.render_times.pop(0)
        
        # Render performance overlay
        self._render_performance_overlay(screen)
        
    def _render_performance_overlay(self, screen: pygame.Surface):
        """Render detailed performance statistics and information."""
        if not self.font or not self.update_times:
            return
            
        # Calculate comprehensive metrics
        avg_update_time = sum(self.update_times) / len(self.update_times)
        min_update_time = min(self.update_times)
        max_update_time = max(self.update_times)
        
        avg_render_time = sum(self.render_times) / len(self.render_times) if self.render_times else 0
        
        total_frame_time = avg_update_time + avg_render_time
        estimated_fps = 1.0 / total_frame_time if total_frame_time > 0 else 0
        
        # Prepare detailed information
        info_lines = [
            f"Entities: {len(self.entities)}",
            f"Update: {avg_update_time*1000:.2f}ms (min: {min_update_time*1000:.1f}, max: {max_update_time*1000:.1f})",
            f"Render: {avg_render_time*1000:.2f}ms",
            f"Total Frame: {total_frame_time*1000:.2f}ms",
            f"Est. FPS: {estimated_fps:.1f}",
        ]
        
        # Add threading information
        threading_status = "ON" if self.threading_enabled else "OFF"
        info_lines.append(f"Threading: {threading_status}")
        
        if hasattr(self, '_thread_pool') and self._thread_pool:
            info_lines.append(f"Workers: {self._thread_pool.max_workers}")
            
        # Add runtime information
        if self.start_time:
            runtime = time.time() - self.start_time
            info_lines.append(f"Runtime: {runtime:.1f}s")
            
        # Render main info panel
        self._render_info_panel(screen, info_lines, 10, 10)
        
        # Render instructions
        instructions = [
            "Controls:",
            "  ESC - Exit demo",
            "  Watch performance metrics",
            "",
            "Features:",
            "  • Multi-threaded entity updates",
            "  • Real-time performance monitoring", 
            "  • Adaptive visual effects",
            "  • Realistic physics simulation"
        ]
        
        self._render_info_panel(screen, instructions, 10, screen.get_height() - 220, self.small_font)
        
    def _render_info_panel(self, screen: pygame.Surface, lines: list, x: int, y: int, font=None):
        """Render an information panel with background."""
        if not lines:
            return
            
        font = font or self.font
        
        # Calculate panel dimensions
        line_height = 25 if font == self.font else 20
        panel_width = max(font.size(line)[0] for line in lines) + 20
        panel_height = len(lines) * line_height + 10
        
        # Draw semi-transparent background
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.set_alpha(200)
        panel_surface.fill((0, 0, 0))
        screen.blit(panel_surface, (x, y))
        
        # Draw border
        pygame.draw.rect(screen, (100, 100, 100), (x, y, panel_width, panel_height), 2)
        
        # Render text lines
        for i, line in enumerate(lines):
            if line.strip():  # Skip empty lines for spacing
                text_surface = font.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (x + 10, y + 5 + i * line_height))
    
    def handle_event(self, event: pygame.event.Event):
        """Handle scene-specific events."""
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Exit the demo
                if hasattr(self, 'interface') and self.interface:
                    self.interface.running = False