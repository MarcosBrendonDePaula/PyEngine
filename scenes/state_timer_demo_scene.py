import pygame
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.rectangle_renderer import RectangleRenderer
from engine.core.components.keyboard_controller import KeyboardController
from engine.core.components.state_machine_component import StateMachineComponent
from engine.core.components.timer_component import TimerComponent
from engine.core.input import input_manager

class StateTimerDemoScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.background_color = (50, 50, 50)

        # Create a demo entity
        player = Entity(100, 100)
        player.add_component(RectangleRenderer(100, 100, (255, 0, 0)))
        player.add_component(KeyboardController())
        self.add_entity(player)

        # Add StateMachineComponent to the player
        def on_idle_enter(entity, data):
            print(f"Player entered IDLE state. Data: {data}")
            entity.get_component(RectangleRenderer).color = (255, 0, 0) # Red

        def on_walking_enter(entity, data):
            print(f"Player entered WALKING state. Data: {data}")
            entity.get_component(RectangleRenderer).color = (0, 255, 0) # Green

        def on_attack_enter(entity, data):
            print(f"Player entered ATTACK state. Data: {data}")
            entity.get_component(RectangleRenderer).color = (0, 0, 255) # Blue

        sm_component = StateMachineComponent(initial_state="idle")
        sm_component.add_state("idle", on_enter=on_idle_enter)
        sm_component.add_state("walking", on_enter=on_walking_enter)
        sm_component.add_state("attack", on_enter=on_attack_enter)
        player.add_component(sm_component)

        # Add TimerComponent to the player
        def attack_timer_callback(entity):
            print("Attack timer finished! Returning to IDLE.")
            entity.get_component(StateMachineComponent).change_state("idle")

        timer_component = TimerComponent()
        timer_component.add_timer("attack_cooldown", 1.5, attack_timer_callback, loop=False, start_immediately=False)
        player.add_component(timer_component)

        self.player = player

    def handle_event(self, event):
        super().handle_event(event)
        sm_component = self.player.get_component(StateMachineComponent)
        timer_component = self.player.get_component(TimerComponent)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                sm_component.change_state("walking", data="forward")
            elif event.key == pygame.K_a:
                sm_component.change_state("walking", data="left")
            elif event.key == pygame.K_s:
                sm_component.change_state("walking", data="backward")
            elif event.key == pygame.K_d:
                sm_component.change_state("walking", data="right")
            elif event.key == pygame.K_SPACE:
                if sm_component.get_current_state() != "attack":
                    sm_component.change_state("attack")
                    timer_component.start_timer("attack_cooldown")

        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
                if sm_component.get_current_state() == "walking":
                    sm_component.change_state("idle")

    def update(self):
        super().update()
        # The tick method of components is called automatically by the entity's update method

    def render(self, screen):
        super().render(screen)
        font = pygame.font.Font(None, 36)
        sm_component = self.player.get_component(StateMachineComponent)
        state_text = font.render(f"Current State: {sm_component.get_current_state()}", True, (255, 255, 255))
        screen.blit(state_text, (10, 10))

        timer_component = self.player.get_component(TimerComponent)
        if timer_component.is_timer_running("attack_cooldown"):
            time_left = timer_component.get_time_left("attack_cooldown")
            timer_text = font.render(f"Attack Cooldown: {time_left:.2f}s", True, (255, 255, 255))
            screen.blit(timer_text, (10, 50))


