from engine.core.component import Component
from typing import Callable, Dict
import pygame

class TimerComponent(Component):
    def __init__(self):
        super().__init__()
        self._timers: Dict[str, Dict[str, Any]] = {}

    def add_timer(self, name: str, duration: float, callback: Callable, loop: bool = False, start_immediately: bool = True):
        self._timers[name] = {
            "duration": duration,
            "callback": callback,
            "loop": loop,
            "time_left": duration if start_immediately else 0,
            "running": start_immediately
        }

    def start_timer(self, name: str):
        if name in self._timers:
            self._timers[name]["running"] = True
            self._timers[name]["time_left"] = self._timers[name]["duration"]

    def pause_timer(self, name: str):
        if name in self._timers:
            self._timers[name]["running"] = False

    def resume_timer(self, name: str):
        if name in self._timers:
            self._timers[name]["running"] = True

    def cancel_timer(self, name: str):
        if name in self._timers:
            del self._timers[name]

    def tick(self):
        delta_time = self.entity.scene.delta_time if self.entity and self.entity.scene else 0.016 # Default to ~60 FPS
        timers_to_trigger = []
        timers_to_delete = []

        for name, timer in self._timers.items():
            if timer["running"]:
                timer["time_left"] -= delta_time
                if timer["time_left"] <= 0:
                    timers_to_trigger.append(name)
                    if timer["loop"]:
                        timer["time_left"] = timer["duration"]
                    else:
                        timers_to_delete.append(name)
        
        for name in timers_to_trigger:
            if name in self._timers: # Check if not deleted by another timer's callback
                self._timers[name]["callback"](self.entity)

        for name in timers_to_delete:
            self.cancel_timer(name)

    def is_timer_running(self, name: str) -> bool:
        return name in self._timers and self._timers[name]["running"]

    def get_time_left(self, name: str) -> float:
        return self._timers[name]["time_left"] if name in self._timers else 0.0


