import pygame
from ..component import Component

class GamepadController(Component):
    def __init__(self, index: int = 0, speed: float = 5.0):
        super().__init__()
        self.index = index
        self.speed = speed
        pygame.joystick.init()
        self.joystick = None
        if pygame.joystick.get_count() > index:
            self.joystick = pygame.joystick.Joystick(index)
            self.joystick.init()

    def tick(self):
        if not self.enabled or not self.entity or not self.joystick:
            return
        pygame.event.pump()
        dx = self.joystick.get_axis(0)
        dy = self.joystick.get_axis(1)
        self.entity.move(dx * self.speed, dy * self.speed)
