import pygame
import os
from engine.core.component import Component
from engine.core.resource_manager import ResourceManager

class TextureRenderer(Component):
    def __init__(self):
        super().__init__()
        self.texture = None
        self.texture_key = ""
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.color = (255, 255, 255)  # Branco padrão (sem alteração de cor)
        self.resource_manager = ResourceManager.get_instance()

    def load_texture(self, path_or_key: str, alias: str = None, colorkey=None):
        """
        Carrega uma textura usando o ResourceManager para cache.
        
        Args:
            path_or_key: Caminho para a textura ou chave para textura já carregada
            alias: Nome alternativo para a textura (opcional)
            colorkey: Cor chave para transparência (opcional)
            
        Returns:
            bool: True se a textura foi carregada com sucesso
        """
        key = alias or path_or_key
        self.texture_key = key
        
        # Verifica se é um caminho ou uma chave
        if os.path.exists(path_or_key):
            # É um caminho, carrega usando ResourceManager
            self.texture = self.resource_manager.load_texture(path_or_key, key, colorkey)
            return self.texture is not None
        else:
            # Tenta obter do ResourceManager como uma chave
            self.texture = self.resource_manager.get_resource(path_or_key)
            if self.texture:
                return True
            else:
                print(f"[TextureRenderer] Recurso não encontrado: {path_or_key}")
                return False

    def set_scale(self, x: float, y: float):
        self.scale_x = x
        self.scale_y = y

    def set_color(self, color: tuple):
        self.color = color
        
    def set_texture(self, texture):
        """
        Define a textura diretamente.
        
        Args:
            texture: A textura a ser usada
        """
        self.texture = texture

    def update(self, dt):
        pass

    def render(self, screen, position):
        if self.texture:
            # Usa o ResourceManager para obter a textura transformada
            texture = self.resource_manager.get_transformed_texture(
                self.texture_key,
                scale=(self.scale_x, self.scale_y) if (self.scale_x != 1.0 or self.scale_y != 1.0) else None,
                color=self.color if self.color != (255, 255, 255) else None
            )
            
            # Se não conseguiu obter a transformada, usa a original
            if not texture:
                texture = self.texture
                
                # Escala
                if self.scale_x != 1.0 or self.scale_y != 1.0:
                    width = int(self.texture.get_width() * self.scale_x)
                    height = int(self.texture.get_height() * self.scale_y)
                    texture = pygame.transform.scale(self.texture, (width, height))
                
                # Cor
                if self.color != (255, 255, 255):
                    texture = texture.copy()
                    texture.fill(self.color, special_flags=pygame.BLEND_MULT)

            screen.blit(texture, position)

    def clear_cache(self):
        """Limpa o cache de texturas do ResourceManager."""
        self.resource_manager.clear_cache()
