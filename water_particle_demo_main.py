import pygame
from engine.core.interface import Interface
from engine.core.scenes.scene_manager import SceneManager
from scenes.water_particle_scene import WaterParticleScene


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Water Particle Demo")

    interface = Interface(screen)

    scene_manager = SceneManager()
    scene_manager.set_interface(interface)
    scene_manager.add_scene("water", WaterParticleScene())
    scene_manager.set_scene("water", transition=False)

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            else:
                scene_manager.handle_event(event)

        scene_manager.update()
        screen.fill((0, 0, 0))
        scene_manager.render(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
