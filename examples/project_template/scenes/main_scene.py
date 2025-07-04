"""
Scene principal do projeto
Customize esta scene para seu jogo específico
"""

import pygame
from engine import BaseScene, Entity, Component

class MainScene(BaseScene):
    """Scene principal do jogo."""
    
    def __init__(self):
        super().__init__()
        self.font = None
        
    def on_initialize(self):
        """Inicializar recursos da scene."""
        print("Inicializando scene principal...")
        
        # Inicializar fonte para UI
        pygame.font.init()
        self.font = pygame.font.Font(None, 48)
        
        # TODO: Adicionar suas entidades aqui
        # Exemplo:
        # player = Entity(512, 384)  # Centro da tela
        # player.add_component(PlayerController())
        # self.add_entity(player)
        
        print("Scene principal inicializada")
        
    def update(self, delta_time: float):
        """Update da scene (com threading automático para entidades)."""
        super().update(delta_time)
        
        # TODO: Adicionar sua lógica de jogo aqui
        # Esta função é chamada a cada frame
        pass
        
    def render(self, screen: pygame.Surface):
        """Render da scene."""
        # Limpar tela com cor de fundo
        screen.fill((64, 128, 255))  # Azul céu
        
        # Renderizar entidades (automático)
        super().render(screen)
        
        # TODO: Adicionar seu render customizado aqui
        self._render_ui(screen)
        
    def _render_ui(self, screen: pygame.Surface):
        """Renderizar interface do usuário."""
        if not self.font:
            return
            
        # Título de exemplo
        title_text = self.font.render("Meu Projeto PyEngine", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(title_text, title_rect)
        
        # Instruções
        instruction_font = pygame.font.Font(None, 24)
        instructions = [
            "Customize este template para seu jogo",
            "Adicione entidades em on_initialize()",
            "Implemente lógica em update()",
            "Adicione rendering em render()",
            "ESC para sair"
        ]
        
        y_start = screen.get_height() // 2
        for i, instruction in enumerate(instructions):
            text = instruction_font.render(instruction, True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen.get_width() // 2, y_start + i * 30))
            screen.blit(text, text_rect)
    
    def handle_event(self, event: pygame.event.Event):
        """Processar eventos."""
        super().handle_event(event)
        
        # TODO: Adicionar seus controles aqui
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Sair do jogo
                if self.interface:
                    self.interface.running = False