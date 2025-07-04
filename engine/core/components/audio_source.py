import pygame
import math
from ..component import Component
from ..audio_manager import init_audio

class AudioSourceComponent(Component):
    def __init__(self, audio_path, max_distance=500, min_distance=50, is_directional=True, direction=0):
        super().__init__()
        self.audio_path = audio_path
        self.max_distance = max_distance  # Distância onde o som fica inaudível
        self.min_distance = min_distance  # Distância de volume máximo
        self.is_directional = is_directional  # Se True, som é direcional. Se False, é global
        self.direction = math.radians(direction)  # Direção da fonte em radianos (0 = direita)
        
        # Ensure mixer initialized once via audio manager
        init_audio()
            
        # Carregar e configurar o som
        self.sound = pygame.mixer.Sound(audio_path)
        self.channel = None
        self.is_playing = False
        
    def set_directional(self, is_directional):
        """Define se o som é direcional ou global"""
        self.is_directional = is_directional
        
    def set_direction(self, angle_degrees):
        """Define a direção da fonte de áudio (apenas para modo direcional)"""
        self.direction = math.radians(angle_degrees)
        
    def play(self, loops=-1):
        """Inicia a reprodução do áudio"""
        if not self.is_playing:
            self.channel = self.sound.play(loops=loops)
            self.is_playing = True
            
    def stop(self):
        """Para a reprodução do áudio"""
        if self.is_playing and self.channel:
            self.channel.stop()
            self.is_playing = False
            
    def get_position(self):
        """Retorna a posição da fonte de áudio"""
        if self.entity:
            return (self.entity.position.x, self.entity.position.y)
        return (0, 0)
            
    def calculate_spatial_properties(self, listener_pos):
        """Calcula propriedades espaciais do áudio em relação ao ouvinte"""
        source_pos = self.get_position()
        dx = source_pos[0] - listener_pos[0]
        dy = source_pos[1] - listener_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Normalizar coordenadas relativas
        if distance > 0:
            dx = dx / distance
            dy = dy / distance
        
        # Calcular volume baseado na distância
        if distance <= self.min_distance:
            volume = 1.0
        elif distance >= self.max_distance:
            volume = 0.0
        else:
            volume = 1.0 - ((distance - self.min_distance) / (self.max_distance - self.min_distance))
            # Aplicar curva quadrática para falloff mais realista
            volume = volume * volume
            
        # Calcular ângulo entre fonte e ouvinte
        angle_to_listener = math.atan2(dy, dx)
        
        # Se a fonte for direcional, calcular o ângulo relativo à direção da fonte
        if self.is_directional:
            # Calcular ângulo relativo
            relative_angle = (angle_to_listener - self.direction) % (2 * math.pi)
            if relative_angle > math.pi:
                relative_angle -= 2 * math.pi
                
            # Calcular fator direcional (1.0 na frente, 0.5 atrás)
            directional_factor = 0.5 + (math.cos(relative_angle) * 0.5)
        else:
            # Som global: mesmo volume em todas as direções
            directional_factor = 1.0
            
        return {
            'distance': distance,
            'dx': dx,
            'dy': dy,
            'base_volume': volume,
            'directional_factor': directional_factor,
            'relative_angle': relative_angle if self.is_directional else 0
        }
            
    def apply_spatial_audio(self, spatial_props, angle_factor):
        """Aplica efeitos de áudio espacial baseado nas propriedades calculadas"""
        if not self.channel:
            return
            
        dx = spatial_props['dx']
        dy = spatial_props['dy']
        base_volume = spatial_props['base_volume']
        directional_factor = spatial_props['directional_factor']
        
        # Distribuição lateral (pan)
        pan = dx
        
        # Atenuação vertical
        vertical_factor = 1.0 - (abs(dy) * 0.3)
        if dy < 0:  # Som vindo de cima
            vertical_factor *= 0.8
            
        # Volume final considerando todos os fatores
        final_volume = base_volume * angle_factor * vertical_factor
        
        if self.is_directional:
            # Aplicar fator direcional ao volume
            final_volume *= directional_factor
            
            # Simular som mais grave atrás da fonte
            relative_angle = spatial_props['relative_angle']
            if abs(relative_angle) > math.pi/2:
                # Som vindo de trás: mais grave
                # Nota: Como pygame não suporta filtros de áudio nativamente,
                # simulamos reduzindo mais as frequências altas (volume)
                # quando o som vem de trás
                back_factor = abs(relative_angle) / math.pi  # 0.5 a 1.0
                final_volume *= (1.0 - (back_factor * 0.3))  # Reduz até 30% atrás
        
        # Aplicar distribuição de volume nos canais
        pan_factor = math.sin(pan * math.pi / 2)
        left_vol = final_volume * (1 - max(0, pan_factor))
        right_vol = final_volume * (1 + min(0, pan_factor))
        
        # Aplicar volumes finais
        self.channel.set_volume(left_vol, right_vol)
            
    def update(self):
        """Atualiza o áudio baseado na posição do ouvinte"""
        if not self.is_playing or not self.channel or not self.entity:
            return
            
        # Procurar por um AudioListenerComponent na cena
        scene = self.entity.scene
        if not scene:
            return
            
        listener = None
        for entity in scene.entities:
            from .audio_listener import AudioListenerComponent
            listener_component = entity.get_component(AudioListenerComponent)
            if listener_component:
                listener = listener_component
                break
                
        if not listener:
            # Se não houver ouvinte, usar volume máximo
            self.channel.set_volume(1.0)
            return
            
        # Calcular propriedades espaciais
        spatial_props = self.calculate_spatial_properties(listener.get_position())
        
        # Obter fator de ângulo do ouvinte
        angle_factor = listener.calculate_angle_factor(self.get_position())
        
        # Aplicar áudio espacial
        self.apply_spatial_audio(spatial_props, angle_factor)
    
    def detach(self):
        """Limpa recursos quando o componente é removido"""
        self.stop()
        super().detach()
