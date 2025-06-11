import pygame

def init_audio():
    """Initialize pygame mixer if not already initialized"""
    if not pygame.mixer.get_init():
        pygame.mixer.init()
