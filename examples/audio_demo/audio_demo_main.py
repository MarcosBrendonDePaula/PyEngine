import pygame
import sys
from engine.core.scenes.scene_manager import SceneManager
from .audio_demo_scene import AudioDemoScene

def main():
    # Initialize Pygame
    pygame.init()
    
    # Create window
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Positional Audio Demo")
    
    # Create and set up scene manager
    scene_manager = SceneManager()
    
    # Add and set the scene
    scene_manager.add_scene("audio_demo", AudioDemoScene())
    scene_manager.set_scene("audio_demo", transition=False)
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            else:
                scene_manager.handle_event(event)
        
        # Update
        scene_manager.update()
        
        # Render
        screen.fill((0, 0, 0))
        scene_manager.render(screen)
        pygame.display.flip()
        
        # Cap at 60 FPS
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
