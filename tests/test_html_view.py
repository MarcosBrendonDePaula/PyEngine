import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pygame
import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
pygame.init()
pygame.display.set_mode((1, 1))

from engine.core.components.ui.html_view import HTMLView


def test_nested_tags_parse():
    view = HTMLView(0, 0, 200, 200)
    view.set_html("<p><b>bold</b><i>italic</i></p>")
    p = view.root.children[0]
    tags = [child.tag for child in p.children]
    assert tags == ["b", "i"]


def test_word_parent_style_preserved():
    view = HTMLView(0, 0, 300, 100)
    view.set_html('<p style="color:#ff0000">hello world</p>')
    parents = {elem.parent.tag for elem in view.elements if elem.tag == "text"}
    assert parents == {"p"}


def test_self_closing_br_img():
    view = HTMLView(0, 0, 200, 200)
    view.set_html('<p>line1<br/>mid<img src="img.png" />end</p>')
    p = view.root.children[0]
    tags = [child.tag for child in p.children]
    assert tags == ["text", "br", "text", "img", "text"]


def test_onclick_event_trigger():
    view = HTMLView(0, 0, 200, 50)
    triggered = []
    view.register_handler("cb", lambda: triggered.append(True))
    view.set_html('<p><span onclick="cb">click</span></p>')
    target = next(e for e in view.elements if e.events.get("onclick"))
    pos = (target.x + 1, target.y + 1)
    view.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": pos, "button": 1}))
    view.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, {"pos": pos, "button": 1}))
    assert triggered == [True]


def test_hover_events():
    view = HTMLView(0, 0, 200, 50)
    events = []
    view.register_handler("enter", lambda: events.append("enter"))
    view.register_handler("leave", lambda: events.append("leave"))
    view.set_html('<p><span onmouseover="enter" onmouseout="leave">hover</span></p>')
    target = next(e for e in view.elements if e.events.get("onmouseover"))
    inside = (target.x + 1, target.y + 1)
    outside = (target.x + target.width + 10, target.y + 1)
    view.handle_event(pygame.event.Event(pygame.MOUSEMOTION, {"pos": inside}))
    view.handle_event(pygame.event.Event(pygame.MOUSEMOTION, {"pos": outside}))
    assert events == ["enter", "leave"]
