import pygame
from typing import Optional, Tuple
from .entity import Entity

class Sprite(Entity):
    def __init__(self, x: float = 0, y: float = 0, image_path: Optional[str] = None):
        super().__init__(x, y)
        self.image: Optional[pygame.Surface] = None
        self.original_image: Optional[pygame.Surface] = None
        self.rect: Optional[pygame.Rect] = None
        
        if image_path:
            self.load_image(image_path)

    def load_image(self, image_path: str):
        """Load an image from a file path"""
        try:
            self.original_image = pygame.image.load(image_path).convert_alpha()
            self.image = self.original_image
            self.rect = self.image.get_rect()
            self.rect.center = self.position
        except pygame.error as e:
            print(f"Could not load image {image_path}: {e}")

    def set_scale(self, scale_x: float, scale_y: float):
        """Scale the sprite's image"""
        if self.original_image:
            new_width = int(self.original_image.get_width() * scale_x)
            new_height = int(self.original_image.get_height() * scale_y)
            self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
            self.rect = self.image.get_rect(center=self.rect.center)
            self.scale.x = scale_x
            self.scale.y = scale_y

    def set_rotation(self, angle: float):
        """Rotate the sprite's image"""
        if self.original_image:
            self.rotation = angle
            self.image = pygame.transform.rotate(self.original_image, -angle)  # Negative for clockwise rotation
            self.rect = self.image.get_rect(center=self.rect.center)

    def get_rect(self) -> pygame.Rect:
        """Override get_rect to use the sprite's rect"""
        if self.rect:
            self.rect.center = self.position
            return self.rect
        return super().get_rect()

    def render(self, screen: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)):
        """Render the sprite to the screen"""
        if not self.visible or not self.image:
            return

        render_pos = (
            self.position.x - camera_offset[0],
            self.position.y - camera_offset[1]
        )
        
        # Only render if the sprite is within the screen bounds
        screen_rect = screen.get_rect()
        sprite_rect = self.get_rect()
        sprite_rect.center = render_pos
        
        if screen_rect.colliderect(sprite_rect):
            screen.blit(self.image, sprite_rect)
