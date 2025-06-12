import pygame
from engine.core.scenes.scene_manager import SceneManager
from .day_night_cycle_scene import DayNightCycleScene

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Day/Night Cycle Demo")
    
    # Create interface mock for the scene manager
    class Interface:
        def __init__(self, screen):
            self.screen = screen
            self.size = screen.get_size()
    
    interface = Interface(screen)
    
    scene_manager = SceneManager()
    scene_manager.set_interface(interface)
    scene_manager.add_scene("day_night", DayNightCycleScene())
    scene_manager.set_scene("day_night", transition=False)
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            scene_manager.handle_event(event)
        
        clock.tick(60)  # Maintain 60 FPS
        
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Update and render
        scene_manager.update()
        scene_manager.render(screen)
        
        pygame.display.flip()
    
    scene_manager.cleanup()
    pygame.quit()

if __name__ == "__main__":
    main()
