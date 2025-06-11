import pygame
from engine.core.scenes.scene_manager import SceneManager
from scenes.liquid_demo_scene import LiquidDemoScene


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Liquid Simulator Demo")

    scene_manager = SceneManager()
    scene_manager.add_scene("liquid", LiquidDemoScene())
    scene_manager.set_scene("liquid", transition=False)

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            scene_manager.handle_event(event)

        scene_manager.update()
        screen.fill((0, 0, 0))
        scene_manager.render(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
