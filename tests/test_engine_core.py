import unittest
import pygame
from unittest.mock import Mock, patch

from engine.core.entity import Entity
from engine.core.component import Component
from engine.core.input import Input
from engine.core.components.state_machine_component import StateMachineComponent
from engine.core.components.timer_component import TimerComponent

class TestEntity(unittest.TestCase):
    def setUp(self):
        self.entity = Entity()

    def test_add_component(self):
        mock_component = Mock(spec=Component)
        self.entity.add_component(mock_component)
        self.assertIn(type(mock_component), self.entity.components)
        mock_component.attach.assert_called_once_with(self.entity)

    def test_add_existing_component_raises_error(self):
        mock_component = Mock(spec=Component)
        self.entity.add_component(mock_component)
        with self.assertRaises(ValueError):
            self.entity.add_component(mock_component)

    def test_get_component(self):
        mock_component = Mock(spec=Component)
        self.entity.add_component(mock_component)
        retrieved_component = self.entity.get_component(type(mock_component))
        self.assertEqual(retrieved_component, mock_component)

    def test_get_non_existent_component(self):
        retrieved_component = self.entity.get_component(Mock(spec=Component))
        self.assertIsNone(retrieved_component)

    def test_remove_component(self):
        mock_component = Mock(spec=Component)
        self.entity.add_component(mock_component)
        self.entity.remove_component(type(mock_component))
        self.assertNotIn(type(mock_component), self.entity.components)
        mock_component.detach.assert_called_once()

    def test_remove_non_existent_component(self):
        # Should not raise an error if component doesn't exist
        self.entity.remove_component(Mock(spec=Component))

    def test_has_component(self):
        mock_component = Mock(spec=Component)
        self.entity.add_component(mock_component)
        self.assertTrue(self.entity.has_component(type(mock_component)))
        self.assertFalse(self.entity.has_component(Mock(spec=Component)))

class TestInput(unittest.TestCase):
    def setUp(self):
        self.input_manager = Input()

    def test_key_down_up_pressed(self):
        # Simulate KEYDOWN event
        event_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        self.input_manager.handle_event(event_down)
        self.assertTrue(self.input_manager.is_key_down(pygame.K_SPACE))
        self.assertTrue(self.input_manager.is_key_pressed(pygame.K_SPACE))
        self.assertFalse(self.input_manager.is_key_up(pygame.K_SPACE))

        # Update frame, key_down should be false, key_pressed true
        self.input_manager.update()
        self.assertFalse(self.input_manager.is_key_down(pygame.K_SPACE))
        self.assertTrue(self.input_manager.is_key_pressed(pygame.K_SPACE))

        # Simulate KEYUP event
        event_up = pygame.event.Event(pygame.KEYUP, key=pygame.K_SPACE)
        self.input_manager.handle_event(event_up)
        self.assertFalse(self.input_manager.is_key_pressed(pygame.K_SPACE))
        self.assertTrue(self.input_manager.is_key_up(pygame.K_SPACE))

        # Update frame, all should be false
        self.input_manager.update()
        self.assertFalse(self.input_manager.is_key_down(pygame.K_SPACE))
        self.assertFalse(self.input_manager.is_key_pressed(pygame.K_SPACE))
        self.assertFalse(self.input_manager.is_key_up(pygame.K_SPACE))

    def test_mouse_button_down_up_pressed(self):
        # Simulate MOUSEBUTTONDOWN event
        event_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1)
        self.input_manager.handle_event(event_down)
        self.assertTrue(self.input_manager.is_mouse_button_down(1))
        self.assertTrue(self.input_manager.is_mouse_button_pressed(1))
        self.assertFalse(self.input_manager.is_mouse_button_up(1))

        # Update frame
        self.input_manager.update()
        self.assertFalse(self.input_manager.is_mouse_button_down(1))
        self.assertTrue(self.input_manager.is_mouse_button_pressed(1))

        # Simulate MOUSEBUTTONUP event
        event_up = pygame.event.Event(pygame.MOUSEBUTTONUP, button=1)
        self.input_manager.handle_event(event_up)
        self.assertFalse(self.input_manager.is_mouse_button_pressed(1))
        self.assertTrue(self.input_manager.is_mouse_button_up(1))

        # Update frame
        self.input_manager.update()
        self.assertFalse(self.input_manager.is_mouse_button_down(1))
        self.assertFalse(self.input_manager.is_mouse_button_pressed(1))
        self.assertFalse(self.input_manager.is_mouse_button_up(1))

    def test_mouse_motion_and_wheel(self):
        event_motion = pygame.event.Event(pygame.MOUSEMOTION, pos=(100, 200), rel=(10, 20))
        self.input_manager.handle_event(event_motion)
        self.assertEqual(self.input_manager.mouse_position, (100, 200))
        self.assertEqual(self.input_manager.mouse_motion, (10, 20))

        event_wheel = pygame.event.Event(pygame.MOUSEWHEEL, y=1)
        self.input_manager.handle_event(event_wheel)
        self.assertEqual(self.input_manager.mouse_wheel, 1)

        self.input_manager.update()
        self.assertEqual(self.input_manager.mouse_motion, (0, 0))
        self.assertEqual(self.input_manager.mouse_wheel, 0)

class TestStateMachineComponent(unittest.TestCase):
    def setUp(self):
        self.entity = Mock()
        self.entity.scene = Mock()
        self.entity.scene.delta_time = 0.016
        self.sm_component = StateMachineComponent(initial_state="idle")
        self.sm_component.attach(self.entity)

    def test_initial_state(self):
        self.assertEqual(self.sm_component.get_current_state(), "idle")

    def test_add_state(self):
        on_enter_mock = Mock()
        self.sm_component.add_state("walking", on_enter=on_enter_mock)
        self.sm_component.change_state("walking")
        self.assertEqual(self.sm_component.get_current_state(), "walking")
        on_enter_mock.assert_called_once_with(self.entity, None)

    def test_change_state_calls_on_exit_and_on_enter(self):
        on_idle_exit = Mock()
        on_attack_enter = Mock()
        self.sm_component.add_state("idle", on_exit=on_idle_exit)
        self.sm_component.add_state("attack", on_enter=on_attack_enter)

        self.sm_component.change_state("attack", data="sword_swing")
        on_idle_exit.assert_called_once_with(self.entity, None)
        on_attack_enter.assert_called_once_with(self.entity, "sword_swing")
        self.assertEqual(self.sm_component.get_current_state(), "attack")
        self.assertEqual(self.sm_component.get_state_data(), "sword_swing")

    def test_change_to_undefined_state_raises_error(self):
        with self.assertRaises(ValueError):
            self.sm_component.change_state("undefined_state")

    def test_tick_calls_on_tick(self):
        on_tick_mock = Mock()
        self.sm_component.add_state("idle", on_tick=on_tick_mock)
        self.sm_component.tick()
        on_tick_mock.assert_called_once_with(self.entity, None)

class TestTimerComponent(unittest.TestCase):
    def setUp(self):
        self.entity = Mock()
        self.entity.scene = Mock()
        self.entity.scene.delta_time = 1.0 # Use 1 second for easier testing
        self.timer_component = TimerComponent()
        self.timer_component.attach(self.entity)

    def test_add_single_timer(self):
        callback_mock = Mock()
        self.timer_component.add_timer("test_timer", 2.0, callback_mock)
        self.assertTrue(self.timer_component.is_timer_running("test_timer"))
        self.assertEqual(self.timer_component.get_time_left("test_timer"), 2.0)

        self.timer_component.tick() # 1 second passes
        self.assertEqual(self.timer_component.get_time_left("test_timer"), 1.0)

        self.timer_component.tick() # 1 second passes, timer should trigger and be removed
        callback_mock.assert_called_once_with(self.entity)
        self.assertFalse(self.timer_component.is_timer_running("test_timer"))

    def test_add_looping_timer(self):
        callback_mock = Mock()
        self.timer_component.add_timer("loop_timer", 1.0, callback_mock, loop=True)

        self.timer_component.tick() # 1 second passes, first trigger
        callback_mock.assert_called_once_with(self.entity)
        self.assertTrue(self.timer_component.is_timer_running("loop_timer"))
        self.assertEqual(self.timer_component.get_time_left("loop_timer"), 1.0)

        callback_mock.reset_mock()
        self.timer_component.tick() # 1 second passes, second trigger
        callback_mock.assert_called_once_with(self.entity)

    def test_pause_resume_timer(self):
        callback_mock = Mock()
        self.timer_component.add_timer("pause_timer", 3.0, callback_mock)

        self.timer_component.tick() # 1 second passes
        self.assertEqual(self.timer_component.get_time_left("pause_timer"), 2.0)

        self.timer_component.pause_timer("pause_timer")
        self.timer_component.tick() # Should not tick down
        self.assertEqual(self.timer_component.get_time_left("pause_timer"), 2.0)

        self.timer_component.resume_timer("pause_timer")
        self.timer_component.tick() # 1 second passes
        self.assertEqual(self.timer_component.get_time_left("pause_timer"), 1.0)

    def test_cancel_timer(self):
        callback_mock = Mock()
        self.timer_component.add_timer("cancel_timer", 2.0, callback_mock)
        self.assertTrue(self.timer_component.is_timer_running("cancel_timer"))

        self.timer_component.cancel_timer("cancel_timer")
        self.assertFalse(self.timer_component.is_timer_running("cancel_timer"))
        self.timer_component.tick() # Should not trigger callback
        callback_mock.assert_not_called()

if __name__ == '__main__':
    unittest.main()

