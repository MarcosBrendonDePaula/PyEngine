"""
Exemplo de componente customizado
Use este como template para seus próprios componentes
"""

import pygame
from engine import Component

class ExampleComponent(Component):
    """Exemplo de componente personalizado."""
    
    def __init__(self, example_value: float = 1.0):
        super().__init__()
        self.example_value = example_value
        self.timer = 0.0
        
    def update(self):
        """Update do componente (chamado automaticamente pelo sistema)."""
        if not self.entity:
            return
            
        # Acesso thread-safe ao delta_time
        dt = self.entity.delta_time
        
        # Exemplo de lógica de update
        self.timer += dt
        
        # TODO: Implementar sua lógica aqui
        # Exemplos:
        # - Movimento baseado em input
        # - Animações
        # - Estado do jogo
        # - Física customizada
        
    def render(self, screen: pygame.Surface, camera_offset=(0, 0)):
        """Render do componente (opcional)."""
        if not self.entity:
            return
            
        # TODO: Implementar render customizado aqui
        # Exemplo de render simples:
        pos = (
            int(self.entity.position.x - camera_offset[0]),
            int(self.entity.position.y - camera_offset[1])
        )
        pygame.draw.circle(screen, (255, 0, 0), pos, 10)
        
    def handle_event(self, event: pygame.event.Event):
        """Processar eventos (opcional)."""
        # TODO: Implementar controles customizados aqui
        # Exemplo:
        # if event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_SPACE:
        #         self.do_something()
        pass