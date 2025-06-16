import pygame
import math
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.audio_source import AudioSourceComponent
from engine.core.components.audio_listener import AudioListenerComponent
from engine.core.components.rectangle_renderer import RectangleRenderer
from engine.core.components.keyboard_controller import KeyboardController

class AudioDemoScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.background_color = (128, 128, 128)  # Gray background
        self.listener_direction = 0  # Ângulo em graus (0 = direita)
        self.setup_scene()
        
    def setup_scene(self):
        # Criar o ouvinte (jogador)
        player = Entity(400, 300)  # Posição central
        
        # Adicionar representação visual (quadrado azul)
        player_renderer = RectangleRenderer(30, 30, (0, 0, 255))
        player.add_component(player_renderer)
        
        # Adicionar controle de teclado
        controller = KeyboardController(speed=5.0)
        player.add_component(controller)
        
        # Adicionar componente de ouvinte com FOV de 180 graus
        listener = AudioListenerComponent(fov=180)
        player.add_component(listener)
        
        self.add_entity(player)
        self.player = player
        
        # Lista para armazenar as fontes de áudio
        self.audio_sources = []
        
        # Criar fontes de áudio em um círculo ao redor do jogador
        num_sources = 8
        radius = 200
        for i in range(num_sources):
            angle = (i * 360 / num_sources)
            x = 400 + radius * math.cos(math.radians(angle))
            y = 300 + radius * math.sin(math.radians(angle))
            
            audio_source = Entity(x, y)
            
            # Definir se é direcional ou global
            is_directional = i < num_sources // 2
            
            # Cor baseada no tipo (vermelho=direcional, verde=global)
            color = (255, 0, 0) if is_directional else (0, 255, 0)
            
            # Adicionar representação visual
            renderer = RectangleRenderer(20, 20, color)
            audio_source.add_component(renderer)
            
            # Alternar entre sons para melhor distinção
            audio_file = "assets/menu/click.wav" if i % 2 == 0 else "assets/menu/music.ogg"
            
            # Adicionar componente de fonte de áudio
            # Para fontes direcionais, apontar para fora do círculo
            audio = AudioSourceComponent(audio_file, max_distance=300, min_distance=50, 
                                      is_directional=is_directional, direction=angle)
            audio_source.add_component(audio)
            audio.play()
            
            self.add_entity(audio_source)
            self.audio_sources.append(audio_source)
    
    def handle_event(self, event):
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:  # Rotacionar para esquerda
                self.listener_direction = (self.listener_direction - 15) % 360
                # Atualizar direção do ouvinte
                if hasattr(self, 'player'):
                    listener = self.player.get_component(AudioListenerComponent)
                    if listener:
                        listener.set_direction(self.listener_direction)
            elif event.key == pygame.K_d:  # Rotacionar para direita
                self.listener_direction = (self.listener_direction + 15) % 360
                # Atualizar direção do ouvinte
                if hasattr(self, 'player'):
                    listener = self.player.get_component(AudioListenerComponent)
                    if listener:
                        listener.set_direction(self.listener_direction)
            elif event.key == pygame.K_SPACE:  # Alternar modo das fontes
                for source in self.audio_sources:
                    audio = source.get_component(AudioSourceComponent)
                    if audio:
                        # Inverter o modo
                        audio.set_directional(not audio.is_directional)
                        # Atualizar cor
                        renderer = source.get_component(RectangleRenderer)
                        if renderer:
                            renderer.set_color((255, 0, 0) if audio.is_directional else (0, 255, 0))
    
    def draw_direction_indicator(self, screen, position, angle, color, size=30):
        """Desenha um indicador de direção para uma entidade"""
        # Calcular ponto final da linha de direção
        angle_rad = math.radians(angle)
        end_point = (
            int(position[0] + math.cos(angle_rad) * size),
            int(position[1] - math.sin(angle_rad) * size)
        )
        # Desenhar linha de direção
        pygame.draw.line(screen, color, position, end_point, 2)
        
        # Desenhar pequena seta na ponta
        arrow_size = 8
        arrow_angle1 = angle_rad + math.pi * 3/4  # 135 graus
        arrow_angle2 = angle_rad - math.pi * 3/4  # -135 graus
        
        arrow_point1 = (
            int(end_point[0] + math.cos(arrow_angle1) * arrow_size),
            int(end_point[1] - math.sin(arrow_angle1) * arrow_size)
        )
        arrow_point2 = (
            int(end_point[0] + math.cos(arrow_angle2) * arrow_size),
            int(end_point[1] - math.sin(arrow_angle2) * arrow_size)
        )
        
        pygame.draw.line(screen, color, end_point, arrow_point1, 2)
        pygame.draw.line(screen, color, end_point, arrow_point2, 2)
    
    def render(self, screen):
        """Render the scene"""
        # Preencher fundo
        screen.fill(self.background_color)
        
        # Renderizar todas as entidades
        super().render(screen)
        
        # Desenhar indicadores de direção
        for source in self.audio_sources:
            audio = source.get_component(AudioSourceComponent)
            if audio and audio.is_directional:
                # Calcular posição na tela
                screen_x = source.position.x
                screen_y = source.position.y
                
                # Aplicar offset da câmera se existir
                if self.camera:
                    screen_x -= self.camera.position.x
                    screen_y -= self.camera.position.y
                
                # Desenhar indicador de direção da fonte
                source_pos = (int(screen_x), int(screen_y))
                # Converter direção de radianos para graus
                direction_degrees = math.degrees(audio.direction)
                self.draw_direction_indicator(screen, source_pos, direction_degrees, (255, 165, 0))  # Laranja
        
        # Desenhar indicador de direção do ouvinte
        if hasattr(self, 'player'):
            # Calcular posição na tela
            screen_x = self.player.position.x
            screen_y = self.player.position.y
            
            # Aplicar offset da câmera se existir
            if self.camera:
                screen_x -= self.camera.position.x
                screen_y -= self.camera.position.y
            
            center = (int(screen_x), int(screen_y))
            
            # Desenhar indicador de direção do ouvinte
            self.draw_direction_indicator(screen, center, self.listener_direction, (255, 255, 0), 40)
            
            # Desenhar arco indicando o FOV
            start_angle = self.listener_direction - 90
            pygame.draw.arc(screen, (255, 255, 0), 
                          (center[0] - 40, center[1] - 40, 80, 80),
                          math.radians(start_angle), 
                          math.radians(start_angle + 180), 2)
            
            # Desenhar legenda
            if pygame.font.get_init():
                font = pygame.font.Font(None, 24)
                text1 = font.render("Vermelho = Direcional (seta laranja indica direção)", True, (255, 0, 0))
                text2 = font.render("Verde = Global (som igual em todas direções)", True, (0, 255, 0))
                text3 = font.render("ESPAÇO = Alternar Modo", True, (255, 255, 255))
                screen.blit(text1, (10, 10))
                screen.blit(text2, (10, 30))
                screen.blit(text3, (10, 50))
