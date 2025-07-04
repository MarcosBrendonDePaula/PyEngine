"""
Main Menu Scene for PyEngine Examples Launcher
"""

import pygame
import math
import random
from engine import BaseScene, Entity, Component
from utils.example_launcher import ExampleLauncher, ExampleInfo
from components.menu_component import MenuButton, ExampleCard, ScrollableContainer

class BackgroundParticle(Component):
    """Animated background particle for visual appeal."""
    
    def __init__(self):
        super().__init__()
        self.speed = random.uniform(10, 30)
        self.direction = random.uniform(0, 2 * math.pi)
        self.size = random.uniform(1, 3)
        self.alpha = random.uniform(50, 150)
        self.color = random.choice([
            (100, 150, 255),
            (150, 100, 255),
            (255, 150, 100),
            (100, 255, 150)
        ])
        self.pulse_speed = random.uniform(1, 3)
        self.pulse_timer = 0
        
    def update(self):
        if not self.entity:
            return
            
        dt = self.entity.delta_time
        
        # Move particle
        self.entity.position.x += math.cos(self.direction) * self.speed * dt
        self.entity.position.y += math.sin(self.direction) * self.speed * dt
        
        # Wrap around screen
        if self.entity.position.x < 0:
            self.entity.position.x = 1200
        elif self.entity.position.x > 1200:
            self.entity.position.x = 0
            
        if self.entity.position.y < 0:
            self.entity.position.y = 800
        elif self.entity.position.y > 800:
            self.entity.position.y = 0
            
        # Update pulse
        self.pulse_timer += dt * self.pulse_speed
        
    def render(self, screen: pygame.Surface, camera_offset=(0, 0)):
        if not self.entity:
            return
            
        # Apply pulse effect
        pulse = 1.0 + 0.3 * math.sin(self.pulse_timer)
        current_size = max(1, int(self.size * pulse))
        
        # Apply alpha
        color_with_alpha = (*self.color, int(self.alpha * pulse))
        
        # Create surface for alpha blending
        particle_surface = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, color_with_alpha, (current_size, current_size), current_size)
        
        pos = (
            int(self.entity.position.x - current_size),
            int(self.entity.position.y - current_size)
        )
        screen.blit(particle_surface, pos)

class MainMenuScene(BaseScene):
    """Main menu scene for launching PyEngine examples."""
    
    def __init__(self):
        super().__init__()
        self.launcher = ExampleLauncher()
        
        # UI state
        self.current_category = "All"
        self.scroll_offset = 0
        self.scroll_target = 0
        
        # Visual elements
        self.title_pulse = 0
        self.selected_example = None
        
        # Fonts
        self.title_font = None
        self.subtitle_font = None
        self.info_font = None
        
        # Layout
        self.sidebar_width = 250
        self.content_width = 950
        self.card_spacing = 20
        self.cards_per_row = 3
        
    def on_initialize(self):
        """Initialize the main menu scene."""
        print("Initializing launcher menu...")
        
        # Initialize fonts
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 64)
        self.subtitle_font = pygame.font.Font(None, 32)
        self.info_font = pygame.font.Font(None, 24)
        
        # Create background particles
        self._create_background_particles()
        
        # Create UI elements
        self._create_sidebar()
        self._create_example_cards()
        
        # Create title entity
        self._create_title()
        
        print("✓ Launcher menu initialized")
        
    def _create_background_particles(self):
        """Create animated background particles."""
        for i in range(30):
            particle = Entity(
                random.uniform(0, 1200),
                random.uniform(0, 800)
            )
            particle.add_component(BackgroundParticle())
            self.add_entity(particle, "background")
            
    def _create_title(self):
        """Create the main title entity."""
        title_entity = Entity(600, 80)  # Center top
        self.add_entity(title_entity, "ui")
        
    def _create_sidebar(self):
        """Create sidebar with category buttons."""
        categories = ["All"] + self.launcher.get_all_categories()
        
        y_start = 150
        for i, category in enumerate(categories):
            button_entity = Entity(125, y_start + i * 60)
            
            def make_category_callback(cat):
                return lambda: self._select_category(cat)
            
            button = MenuButton(
                text=category,
                width=200,
                height=45,
                callback=make_category_callback(category),
                color=(60, 60, 80) if category != self.current_category else (100, 149, 237),
                hover_color=(80, 80, 120)
            )
            button_entity.add_component(button)
            self.add_entity(button_entity, "ui")
            
        # Add stats info
        stats = self.launcher.get_example_stats()
        stats_entity = Entity(125, y_start + len(categories) * 60 + 50)
        self.add_entity(stats_entity, "ui")
        self.stats_entity = stats_entity
        
    def _create_example_cards(self):
        """Create example cards based on current category."""
        # Clear existing cards
        for entity in self.get_entities_by_group("cards"):
            self.remove_entity(entity, "cards")
            
        # Get examples for current category
        if self.current_category == "All":
            examples = self.launcher.get_all_examples()
        else:
            examples = self.launcher.get_examples_by_category(self.current_category)
            
        # Create cards
        start_x = self.sidebar_width + 50
        start_y = 150
        card_width = 280
        card_height = 180
        
        for i, example in enumerate(examples):
            row = i // self.cards_per_row
            col = i % self.cards_per_row
            
            x = start_x + col * (card_width + self.card_spacing)
            y = start_y + row * (card_height + self.card_spacing)
            
            card_entity = Entity(x + card_width // 2, y + card_height // 2)
            
            card = ExampleCard(example, card_width, card_height)
            card_entity.add_component(card)
            
            # Store example info for launching
            card_entity.example_info = example
            
            self.add_entity(card_entity, "cards")
            
    def _select_category(self, category: str):
        """Select a category and refresh cards."""
        if category != self.current_category:
            print(f"Selected category: {category}")
            self.current_category = category
            self._create_example_cards()
            self._create_sidebar()  # Refresh sidebar to update selected button
            
    def update(self, delta_time: float):
        """Update the menu scene."""
        super().update(delta_time)
        
        # Update title pulse
        self.title_pulse += delta_time * 2
        
        # Smooth scrolling
        self.scroll_offset += (self.scroll_target - self.scroll_offset) * 5 * delta_time
        
    def render(self, screen: pygame.Surface):
        """Render the menu scene."""
        # Dark gradient background
        for i in range(800):
            color_value = int(20 + (i / 800) * 15)
            color = (color_value, color_value, color_value + 5)
            pygame.draw.line(screen, color, (0, i), (1200, i))
            
        # Render background particles first
        for entity in self.get_entities_by_group("background"):
            if entity.visible:
                entity.render(screen)
                
        # Draw sidebar background
        sidebar_rect = pygame.Rect(0, 0, self.sidebar_width, 800)
        pygame.draw.rect(screen, (25, 25, 35), sidebar_rect)
        pygame.draw.line(screen, (60, 60, 80), (self.sidebar_width, 0), (self.sidebar_width, 800), 2)
        
        # Render main title
        self._render_title(screen)
        
        # Render sidebar content
        self._render_sidebar_content(screen)
        
        # Render cards with scroll offset
        for entity in self.get_entities_by_group("cards"):
            if entity.visible:
                # Apply scroll offset
                original_y = entity.position.y
                entity.position.y -= self.scroll_offset
                entity.render(screen)
                entity.position.y = original_y  # Restore position
                
        # Render UI elements
        for entity in self.get_entities_by_group("ui"):
            if entity.visible:
                entity.render(screen)
                
        # Render instructions
        self._render_instructions(screen)
        
    def _render_title(self, screen: pygame.Surface):
        """Render the main title with effects."""
        # Main title with pulse effect
        pulse = 1.0 + 0.1 * math.sin(self.title_pulse)
        
        title_text = "PyEngine Examples Launcher"
        title_surface = self.title_font.render(title_text, True, (255, 255, 255))
        
        # Scale with pulse
        scaled_width = int(title_surface.get_width() * pulse)
        scaled_height = int(title_surface.get_height() * pulse)
        title_surface = pygame.transform.scale(title_surface, (scaled_width, scaled_height))
        
        title_rect = title_surface.get_rect(center=(600, 80))
        screen.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle_text = "Explore and launch PyEngine demos"
        subtitle_surface = self.subtitle_font.render(subtitle_text, True, (200, 200, 200))
        subtitle_rect = subtitle_surface.get_rect(center=(600, 120))
        screen.blit(subtitle_surface, subtitle_rect)
        
    def _render_sidebar_content(self, screen: pygame.Surface):
        """Render sidebar content."""
        # Sidebar title
        sidebar_title = self.subtitle_font.render("Categories", True, (255, 255, 255))
        screen.blit(sidebar_title, (20, 20))
        
        # Stats
        if hasattr(self, 'stats_entity'):
            stats = self.launcher.get_example_stats()
            stats_lines = [
                f"Total Examples: {stats['total']}",
                f"Categories: {stats['categories']}",
                f"Beginner: {stats['beginner']}",
                f"Intermediate: {stats['intermediate']}",
                f"Advanced: {stats['advanced']}",
                f"Threading Demos: {stats['threading_demos']}"
            ]
            
            y_offset = self.stats_entity.position.y - 50
            for line in stats_lines:
                text_surface = self.info_font.render(line, True, (180, 180, 180))
                screen.blit(text_surface, (20, y_offset))
                y_offset += 25
                
    def _render_instructions(self, screen: pygame.Surface):
        """Render instructions at the bottom."""
        instructions = [
            "Click on example cards to launch them",
            "Use categories to filter examples",
            "Scroll with mouse wheel or arrow keys",
            "ESC to exit launcher"
        ]
        
        y_start = 720
        for i, instruction in enumerate(instructions):
            text_surface = self.info_font.render(instruction, True, (150, 150, 150))
            screen.blit(text_surface, (self.sidebar_width + 20, y_start + i * 20))
            
    def handle_event(self, event: pygame.event.Event):
        """Handle menu events."""
        super().handle_event(event)
        
        # Handle scrolling
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_target = max(0, self.scroll_target - event.y * 30)
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Exit launcher
                if hasattr(self, 'interface') and self.interface:
                    self.interface.running = False
                    
            elif event.key == pygame.K_UP:
                self.scroll_target = max(0, self.scroll_target - 50)
            elif event.key == pygame.K_DOWN:
                self.scroll_target += 50
                
        # Handle card clicks
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self._handle_card_click(event.pos)
                
    def _handle_card_click(self, mouse_pos):
        """Handle clicking on example cards."""
        for entity in self.get_entities_by_group("cards"):
            card_component = entity.get_component(ExampleCard)
            if card_component and card_component.is_hovered:
                # Navigate to code viewer scene
                example_info = entity.example_info
                print(f"Opening code viewer for: {example_info.name}")
                
                if hasattr(self, 'interface') and self.interface:
                    from scenes.code_viewer_scene import CodeViewerScene
                    code_scene = CodeViewerScene(example_info, self.launcher)
                    self.interface.scene_manager.add_scene("code_viewer", code_scene)
                    self.interface.scene_manager.set_scene("code_viewer")
                break