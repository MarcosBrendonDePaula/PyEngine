import pygame
from ..component import Component

class TileMap(Component):
    def __init__(self, tile_size: int, tileset_path: str, map_data):
        super().__init__()
        self.tile_size = tile_size
        self.tileset = pygame.image.load(tileset_path).convert_alpha()
        self.map_data = map_data  # 2D list of tile indices

    def update(self):
        pass  # Static tilemap has no update logic by default

    def render(self, screen: pygame.Surface, offset=(0, 0)):
        if not self.enabled:
            return
        tiles_per_row = self.tileset.get_width() // self.tile_size
        for y, row in enumerate(self.map_data):
            for x, tile in enumerate(row):
                if tile < 0:
                    continue
                sx = (tile % tiles_per_row) * self.tile_size
                sy = (tile // tiles_per_row) * self.tile_size
                rect = pygame.Rect(sx, sy, self.tile_size, self.tile_size)
                screen.blit(
                    self.tileset,
                    (x * self.tile_size - offset[0], y * self.tile_size - offset[1]),
                    rect,
                )
