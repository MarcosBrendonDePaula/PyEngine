import pygame
import math
from ..component import Component

class AudioListenerComponent(Component):
    def __init__(self, fov=180):
        super().__init__()
        self.direction = 0  # Ângulo em radianos (0 = direita)
        self.fov = math.radians(fov)  # Campo de audição em radianos
        
    def set_direction(self, angle_degrees):
        """Define a direção que o ouvinte está olhando"""
        self.direction = math.radians(angle_degrees)
        
    def get_position(self):
        """Retorna a posição do ouvinte"""
        if self.entity:
            return (self.entity.position.x, self.entity.position.y)
        return (0, 0)
        
    def calculate_angle_factor(self, source_pos):
        """Calcula o fator de volume baseado no ângulo da fonte em relação à direção do ouvinte"""
        if not self.entity:
            return 1.0
            
        listener_pos = self.get_position()
        dx = source_pos[0] - listener_pos[0]
        dy = source_pos[1] - listener_pos[1]
        
        # Calcular ângulo entre ouvinte e fonte
        angle_to_source = math.atan2(dy, dx)
        
        # Calcular ângulo relativo
        relative_angle = (angle_to_source - self.direction) % (2 * math.pi)
        if relative_angle > math.pi:
            relative_angle -= 2 * math.pi
            
        # Calcular fator de ângulo usando uma curva cosseno
        # Isso cria uma transição mais suave entre as direções
        if abs(relative_angle) <= self.fov / 2:
            # Som está dentro do FOV
            # Usar cosseno para ter volume máximo quando olhando diretamente para a fonte
            # e diminuir gradualmente conforme o ângulo aumenta
            angle_factor = math.cos(relative_angle * math.pi / self.fov)
            # Normalizar para range 0.5-1.0
            angle_factor = 0.5 + (angle_factor * 0.5)
        else:
            # Som está fora do FOV
            # Volume reduzido mas não completamente silenciado
            angle_factor = 0.3
            
        return angle_factor
