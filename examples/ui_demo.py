import pygame
import sys
from engine.core.interface import Interface
from engine.core.scenes.scene_manager import SceneManager
from examples.scenes.ui_demo_scene import UIDemoScene

def main():
    # Initialize Pygame
    pygame.init()

    # Create window
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("PyEngine UI Demo")

    # Create interface wrapper
    interface = Interface(screen)

    # Create scene manager and add scenes
    scene_manager = SceneManager()
    scene_manager.set_interface(interface)  # Set interface before adding scenes
    scene_manager.add_scene("ui_demo", UIDemoScene())
    scene_manager.set_scene("ui_demo", transition=False)

    # Game loop
    clock = pygame.time.Clock()
    running = True

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                scene_manager.handle_event(event)
        
        # Update
        dt = clock.tick(60) / 1000.0  # Convert to seconds
        scene_manager.update()
        
        # Render
        screen.fill((0, 0, 0))  # Light gray background
        scene_manager.render(screen)
        pygame.display.flip()

    # Quit
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
