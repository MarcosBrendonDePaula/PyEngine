import pygame
import random
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.particle_system import ParticleSystem
from engine.core.components.debug_info import DebugInfoComponent
from engine.core.components.ui.slider import Slider
from engine.core.components.ui.label import Label
from engine.core.components.collider import RectCollider, CircleCollider
from engine.core.components.rectangle_renderer import RectangleRenderer
from engine.core.components.physics import Physics
from engine.core.resource_manager import ResourceManager
from engine import Engine

class WaterParticle(Entity):
    def __init__(self, x, y, radius=3, gravity=500.0):
        super().__init__(x, y)
        self.collider = CircleCollider(radius)
        self.add_component(self.collider)
        
        self.physics = Physics(mass=1.0, gravity=gravity, friction=0.05)
        self.physics.restitution = 0.6  # Bouncy water particles
        self.add_component(self.physics)

class Obstacle(Entity):
    def __init__(self, x, y, width, height, is_static=True):
        super().__init__(x, y)
        self.collider = RectCollider(width, height)
        self.add_component(self.collider)
        
        self.rectangle_render = RectangleRenderer(width, height, (255, 255, 255))
        self.add_component(self.rectangle_render)
        
        self.physics = Physics(mass=10.0, gravity=0.0, friction=0.1)
        if is_static:
            self.physics.set_static(True)  # Impede que se mova e permite colisão
        else:
            self.physics.set_kinematic(True)
        self.add_component(self.physics)

class DebugInfo(Entity):
    def __init__(self):
        super().__init__(0, 0)
        self.add_component(DebugInfoComponent())

class WaterCollisionScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.background_color = (10, 10, 30)
        self.resource_manager = ResourceManager.get_instance()
        self.emitter = Entity(400, 50)
        self.particle_system = None
        self.water_particles = []
        self.obstacles = []
        self.gravity = 500.0  # Increased default gravity
        self.spawn_rate = 5
        self.spawn_spread = 24
        self.max_particles = 1000
        self.particle_radius = 3
        self.show_colliders = True
        self.particle_color = (0, 150, 255)
        
    def load_resources(self):
        """Load resources for the scene"""
        print("Loading resources for WaterCollisionScene")
        
        # Create particle system
        self.emitter = Entity(400, 50)
        self.particle_system = self.emitter.add_component(ParticleSystem(max_particles=self.max_particles))
        self.add_entity(self.emitter)
        
        # Add debug info
        self.add_entity(DebugInfo())
        
        # Create UI controls
        self._create_ui_controls()
        
        # Create obstacles
        self._create_obstacles()
        
        # Mark scene as loaded
        self._is_loaded = True
        self._loading_progress = 100
        print("Resources loaded")
    
    def _create_ui_controls(self):
        """Create UI controls for the demo"""
        # FPS slider
        fps_label = Label(20, 20, "FPS Limit:")
        fps_label.set_text_color((255, 255, 255))
        self.add_entity(fps_label)
        
        fps_slider = Slider(120, 20, 100, 20)
        fps_slider.max_value = 250
        fps_slider.min_value = 10
        fps_slider.value = 60
        fps_slider.on_value_changed = self._change_fps
        self.add_entity(fps_slider)
        
        # Particle count slider
        count_label = Label(20, 50, "Particles:")
        count_label.set_text_color((255, 255, 255))
        self.add_entity(count_label)
        
        count_slider = Slider(120, 50, 100, 20)
        count_slider.max_value = 2000
        count_slider.min_value = 100
        count_slider.value = self.max_particles
        count_slider.on_value_changed = self._change_particle_count
        self.add_entity(count_slider)
        
        # Spawn rate slider
        rate_label = Label(20, 80, "Spawn Rate:")
        rate_label.set_text_color((255, 255, 255))
        self.add_entity(rate_label)
        
        rate_slider = Slider(120, 80, 100, 20)
        rate_slider.max_value = 20
        rate_slider.min_value = 1
        rate_slider.value = self.spawn_rate
        rate_slider.on_value_changed = self._change_spawn_rate
        self.add_entity(rate_slider)
        
        # Gravity slider
        gravity_label = Label(20, 110, "Gravity:")
        gravity_label.set_text_color((255, 255, 255))
        self.add_entity(gravity_label)
        
        gravity_slider = Slider(120, 110, 100, 20)
        gravity_slider.max_value = 1000
        gravity_slider.min_value = 100
        gravity_slider.value = self.gravity
        gravity_slider.on_value_changed = self._change_gravity
        self.add_entity(gravity_slider)
        
        # Instructions
        instructions = [
            "Click and drag to move emitter",
            "Press C to toggle collider visibility",
            "Press R to reset obstacles",
            "Press SPACE to add random obstacle",
            "Use sliders to adjust parameters"
        ]
        
        y = 150
        for instruction in instructions:
            label = Label(20, y, instruction)
            label.set_text_color((200, 200, 200))
            self.add_entity(label)
            y += 25
    
    def _create_obstacles(self):
        """Create initial obstacles"""
        # Floor
        floor = Obstacle(400, 590, 800, 20)
        self.add_entity(floor)
        self.obstacles.append(floor)
        
        # Left wall
        left_wall = Obstacle(5, 300, 10, 600)
        self.add_entity(left_wall)
        self.obstacles.append(left_wall)
        
        # Right wall
        right_wall = Obstacle(795, 300, 10, 600)
        self.add_entity(right_wall)
        self.obstacles.append(right_wall)
        
        # Some platforms
        platform1 = Obstacle(200, 400, 100, 20)
        self.add_entity(platform1)
        self.obstacles.append(platform1)
        
        platform2 = Obstacle(600, 300, 100, 20)
        self.add_entity(platform2)
        self.obstacles.append(platform2)
        
        # Angled obstacle
        angled = Obstacle(400, 200, 200, 20)
        angled.rotation = 30  # Degrees
        self.add_entity(angled)
        self.obstacles.append(angled)
    
    def _change_fps(self, value):
        """Change FPS limit"""
        Engine.ENGINE_INSTANCE.interface.set_fps(int(value))
    
    def _change_particle_count(self, value):
        """Change maximum particle count"""
        self.max_particles = int(value)
        if self.particle_system:
            self.particle_system.max_particles = self.max_particles
    
    def _change_spawn_rate(self, value):
        """Change particle spawn rate"""
        self.spawn_rate = int(value)
        
    def _change_gravity(self, value):
        """Change gravity for water particles"""
        self.gravity = float(value)
        
        # Update gravity for existing particles
        for particle in self.water_particles:
            if particle.physics:
                particle.physics.set_gravity(self.gravity)
    
    def _add_random_obstacle(self):
        """Add a random obstacle"""
        width = random.randint(50, 150)
        height = random.randint(10, 30)
        x = random.randint(width//2, 800 - width//2)
        y = random.randint(height//2, 500)
        
        obstacle = Obstacle(x, y, width, height)
        if random.random() > 0.5:
            obstacle.rotation = random.randint(0, 360)
        
        self.add_entity(obstacle)
        self.obstacles.append(obstacle)
    
    def _reset_obstacles(self):
        """Reset obstacles to initial state"""
        # Remove all obstacles
        for obstacle in self.obstacles:
            self.remove_entity(obstacle)
        self.obstacles.clear()
        
        # Create new obstacles
        self._create_obstacles()
    
    def _toggle_colliders(self):
        """Toggle collider visibility"""
        self.show_colliders = not self.show_colliders
        
        # Update all colliders
        for obstacle in self.obstacles:
            if obstacle.collider:
                obstacle.collider.show_debug = self.show_colliders
        
        for particle in self.water_particles:
            if particle.collider:
                particle.collider.show_debug = self.show_colliders
    
    def handle_event(self, event):
        """Handle input events"""
        super().handle_event(event)
        
        if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
            # Move emitter with mouse when dragging
            self.emitter.position.x = event.pos[0]
            self.emitter.position.y = event.pos[1]
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                # Toggle collider visibility
                self._toggle_colliders()
            elif event.key == pygame.K_r:
                # Reset obstacles
                self._reset_obstacles()
            elif event.key == pygame.K_SPACE:
                # Add random obstacle
                self._add_random_obstacle()
    
    def update(self, delta):
        """Update the scene"""
        super().update(delta)
        if not self._is_loaded:
            return
            
        dt = self.interface.clock.get_time() / 1000.0
        
        # Spawn new water particles
        for _ in range(self.spawn_rate):
            if len(self.water_particles) < self.max_particles:
                offset_x = random.uniform(-self.spawn_spread/2, self.spawn_spread/2)
                
                # Create water particle entity
                particle = WaterParticle(
                    self.emitter.position.x + offset_x,
                    self.emitter.position.y,
                    self.particle_radius,
                    self.gravity
                )
                
                # Set initial velocity
                if particle.physics:
                    particle.physics.set_velocity(
                        random.uniform(-30, 30),
                        random.uniform(0, 50)
                    )
                
                # Set collider visibility
                if particle.collider:
                    particle.collider.show_debug = self.show_colliders
                    particle.collider.set_debug_color(self.particle_color)
                
                # Add to scene
                self.add_entity(particle)
                self.water_particles.append(particle)
                
                # Also emit visual particle
                self.particle_system.emit(
                    (particle.position.x, particle.position.y),
                    (random.uniform(-10, 10), random.uniform(0, 20)),
                    self.particle_color,
                    lifetime=5.0,
                    radius=self.particle_radius
                )
        
        # Remove particles that are too old or out of bounds
        for particle in self.water_particles[:]:
            if (particle.position.y > 1000 or
                particle.position.x < -100 or
                particle.position.x > 900):
                self.remove_entity(particle)
                self.water_particles.remove(particle)
    
    def render(self, screen: pygame.Surface):
        """Render the scene"""
        screen.fill(self.background_color)
        super().render(screen)
