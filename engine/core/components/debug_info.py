import pygame
from ..component import Component

class DebugInfoComponent(Component):
    def __init__(self):
        super().__init__()
        pygame.font.init()
        self.font = pygame.font.Font(None, 24)  # Default system font, size 24
        self.color = (255, 255, 255)  # White text
        self.padding = 10  # Padding from screen edges

    def render(self, screen, camera_offset=(0, 0)):
        if not self.enabled or not self.entity:
            return

        interface = self.entity.scene.interface
        current_fps = int(interface.get_fps())
        entity_count = len(self.entity.scene.entities)

        # Create debug text
        fps_text = self.font.render(f"FPS: {current_fps}", True, self.color)
        entities_text = self.font.render(f"Entities: {entity_count}", True, self.color)

        # Draw text at top-left corner with padding
        screen.blit(fps_text, (self.padding, self.padding))
        screen.blit(entities_text, (self.padding, self.padding + 25))  # 25 pixels below FPS
