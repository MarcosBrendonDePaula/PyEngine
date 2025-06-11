import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
pygame.init()
pygame.display.set_mode((1, 1))

from engine.core.components.ui.html_view import HTMLView


def test_example_event_flow():
    """Demonstrates registering a handler and triggering it via a click"""
    view = HTMLView(0, 0, 200, 50)
    log = []
    view.register_handler("say_hi", lambda: log.append("hi"))
    view.set_html('<p><span onclick="say_hi">Hi</span></p>')

    target = next(e for e in view.elements if e.events.get("onclick"))
    pos = (target.x + 1, target.y + 1)
    view.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": pos, "button": 1}))
    view.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, {"pos": pos, "button": 1}))

    assert log == ["hi"]
