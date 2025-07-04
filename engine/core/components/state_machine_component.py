from engine.core.component import Component
from typing import Dict, Callable, Any

class StateMachineComponent(Component):
    def __init__(self, initial_state: str, states: Dict[str, Dict[str, Callable]] = None):
        super().__init__()
        self._current_state: str = initial_state
        self._states: Dict[str, Dict[str, Callable]] = states if states is not None else {}
        self._state_data: Dict[str, Any] = {}

    def add_state(self, state_name: str, on_enter: Callable = None, on_exit: Callable = None, on_update: Callable = None):
        self._states[state_name] = {
            "on_enter": on_enter,
            "on_exit": on_exit,
            "on_update": on_update
        }

    def change_state(self, new_state_name: str, data: Any = None):
        if new_state_name not in self._states:
            raise ValueError(f"State \'{new_state_name}\' not defined.")

        # Call on_exit for current state
        if self._current_state in self._states and self._states[self._current_state]["on_exit"]:
            self._states[self._current_state]["on_exit"](self.entity, self._state_data.get(self._current_state))

        self._current_state = new_state_name
        self._state_data[new_state_name] = data

        # Call on_enter for new state
        if self._states[self._current_state]["on_enter"]:
            self._states[self._current_state]["on_enter"](self.entity, data)

    def update(self):
        if self._current_state in self._states and self._states[self._current_state]["on_update"]:
            self._states[self._current_state]["on_update"](self.entity, self._state_data.get(self._current_state))

    def get_current_state(self) -> str:
        return self._current_state

    def get_state_data(self, state_name: str = None) -> Any:
        if state_name is None:
            state_name = self._current_state
        return self._state_data.get(state_name)


