from engine.core.component import Component
from typing import Callable

class HealthComponent(Component):
    def __init__(self, max_health: int, current_health: int = None):
        super().__init__()
        self._max_health = max_health
        self._current_health = current_health if current_health is not None else max_health
        self._on_health_changed_callbacks: list[Callable[[int, int], None]] = []
        self._on_death_callbacks: list[Callable[[], None]] = []

    @property
    def max_health(self) -> int:
        return self._max_health

    @max_health.setter
    def max_health(self, value: int):
        if value <= 0:
            raise ValueError("Max health must be positive.")
        self._max_health = value
        self.current_health = min(self._current_health, self._max_health) # Adjust current health if max changes

    @property
    def current_health(self) -> int:
        return self._current_health

    @current_health.setter
    def current_health(self, value: int):
        old_health = self._current_health
        self._current_health = max(0, min(value, self._max_health))
        if old_health != self._current_health:
            for callback in self._on_health_changed_callbacks:
                callback(self._current_health, old_health)
            if self._current_health == 0:
                for callback in self._on_death_callbacks:
                    callback()

    def take_damage(self, amount: int):
        if amount < 0:
            raise ValueError("Damage amount cannot be negative.")
        self.current_health -= amount

    def heal(self, amount: int):
        if amount < 0:
            raise ValueError("Heal amount cannot be negative.")
        self.current_health += amount

    def is_dead(self) -> bool:
        return self._current_health <= 0

    def on_health_changed(self, callback: Callable[[int, int], None]):
        self._on_health_changed_callbacks.append(callback)

    def on_death(self, callback: Callable[[], None]):
        self._on_death_callbacks.append(callback)

    def remove_health_changed_callback(self, callback: Callable[[int, int], None]):
        if callback in self._on_health_changed_callbacks:
            self._on_health_changed_callbacks.remove(callback)

    def remove_death_callback(self, callback: Callable[[], None]):
        if callback in self._on_death_callbacks:
            self._on_death_callbacks.remove(callback)


