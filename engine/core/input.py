import pygame
from typing import Dict, Set, Tuple

class Input:
    def __init__(self):
        self._keys_pressed: Set[int] = set()
        self._keys_down: Set[int] = set()
        self._keys_up: Set[int] = set()
        
        self._mouse_buttons: Set[int] = set()
        self._mouse_buttons_down: Set[int] = set()
        self._mouse_buttons_up: Set[int] = set()
        
        self._mouse_position: Tuple[int, int] = (0, 0)
        self._mouse_motion: Tuple[int, int] = (0, 0)
        self._mouse_wheel: int = 0

    def update(self):
        """Clear one-frame input states"""
        self._keys_down.clear()
        self._keys_up.clear()
        self._mouse_buttons_down.clear()
        self._mouse_buttons_up.clear()
        self._mouse_motion = (0, 0)
        self._mouse_wheel = 0

    def handle_event(self, event: pygame.event.Event):
        """Process pygame events for input"""
        if event.type == pygame.KEYDOWN:
            self._keys_pressed.add(event.key)
            self._keys_down.add(event.key)
        
        elif event.type == pygame.KEYUP:
            self._keys_pressed.discard(event.key)
            self._keys_up.add(event.key)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._mouse_buttons.add(event.button)
            self._mouse_buttons_down.add(event.button)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self._mouse_buttons.discard(event.button)
            self._mouse_buttons_up.add(event.button)
        
        elif event.type == pygame.MOUSEMOTION:
            self._mouse_position = event.pos
            self._mouse_motion = event.rel
        
        elif event.type == pygame.MOUSEWHEEL:
            self._mouse_wheel = event.y

    # Keyboard input methods
    def is_key_pressed(self, key: int) -> bool:
        """Check if a key is being held down"""
        return key in self._keys_pressed

    def is_key_down(self, key: int) -> bool:
        """Check if a key was just pressed this frame"""
        return key in self._keys_down

    def is_key_up(self, key: int) -> bool:
        """Check if a key was just released this frame"""
        return key in self._keys_up

    # Mouse input methods
    def is_mouse_button_pressed(self, button: int) -> bool:
        """Check if a mouse button is being held down"""
        return button in self._mouse_buttons

    def is_mouse_button_down(self, button: int) -> bool:
        """Check if a mouse button was just pressed this frame"""
        return button in self._mouse_buttons_down

    def is_mouse_button_up(self, button: int) -> bool:
        """Check if a mouse button was just released this frame"""
        return button in self._mouse_buttons_up

    @property
    def mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position"""
        return self._mouse_position

    @property
    def mouse_motion(self) -> Tuple[int, int]:
        """Get mouse movement this frame"""
        return self._mouse_motion

    @property
    def mouse_wheel(self) -> int:
        """Get mouse wheel movement this frame"""
        return self._mouse_wheel

# Global input instance
input_manager = Input()
