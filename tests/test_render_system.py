import unittest
from unittest.mock import MagicMock, patch
import pygame

# Mock pygame for testing purposes
pygame.init = MagicMock()
pygame.font = MagicMock()
pygame.font.init = MagicMock()
# Mock pygame.font.Font to return a mock object that has a render method
pygame.font.Font = MagicMock(return_value=MagicMock(render=MagicMock(return_value=MagicMock(get_rect=MagicMock(return_value=MagicMock(x=0, y=0, w=0, h=0))))))

pygame.display = MagicMock()
pygame.display.update = MagicMock()
pygame.display.flip = MagicMock()

# Mock pygame.Rect to return a mock object with expected attributes
# Ensure x, y, w, h are set correctly for tests that check them
class MockRect(MagicMock):
    def __init__(self, x=0, y=0, w=0, h=0, **kwargs):
        super().__init__(**kwargs)
        self._x = x
        self._y = y
        self.w = w
        self.h = h
        self.colliderect = MagicMock(return_value=True)

    def copy(self):
        # Return a new MockRect with the same dimensions
        return MockRect(self._x, self._y, self.w, self.h)

    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, value):
        self._y = value

    @property
    def topleft(self):
        return (self._x, self._y)
    @topleft.setter
    def topleft(self, value):
        self._x = value[0]
        self._y = value[1]

    @property
    def width(self):
        return self.w
    @property
    def height(self):
        return self.h

pygame.Rect = MockRect # Assign our custom mock class to pygame.Rect

# Mock pygame.image.load
pygame.image = MagicMock()
pygame.image.load = MagicMock()

# Mock pygame.mixer.Sound
pygame.mixer = MagicMock()
pygame.mixer.Sound = MagicMock()

# Mock pygame.math.Vector2
pygame.math = MagicMock()
pygame.math.Vector2 = MagicMock(side_effect=lambda x, y: MagicMock(x=x, y=y))

# Mock pygame.Surface as a class that can be instantiated
# And ensure its instances have convert/convert_alpha methods
class MockSurface(MagicMock):
    def convert(self):
        return MockSurface()
    def convert_alpha(self):
        return MockSurface()
    def get_rect(self):
        # Return an instance of our MockRect
        return MockRect(x=0, y=0, w=0, h=0) 

pygame.Surface = MockSurface # Assign our custom mock class to pygame.Surface

# Mock pygame.draw
pygame.draw = MagicMock()
pygame.draw.rect = MagicMock() 

# Import the classes to be tested after mocking pygame
from engine.core.interface import Interface
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.rectangle_renderer import RectangleRenderer
from engine.core.sprite import Sprite

class TestRenderSystem(unittest.TestCase):

    def setUp(self):
        self.mock_screen = MockSurface() # Use our custom mock surface
        # Now get_rect is a method that returns a MockRect, so we can set its return_value
        self.mock_screen.get_rect.return_value = MockRect(x=0, y=0, w=800, h=600, colliderect=MagicMock(return_value=True))
        
        # Reset pygame.display.update mock before each test
        pygame.display.update.reset_mock()

    def test_base_scene_dirty_rects_management(self):
        scene = BaseScene()
        
        rect1 = MockRect() # Use MockRect directly
        rect2 = MockRect() # Use MockRect directly
        rect3 = MockRect() # Use MockRect directly

        scene.add_dirty_rect(rect1)
        self.assertEqual(scene.get_dirty_rects(), [rect1])

        scene.add_dirty_rect(rect2)
        self.assertEqual(scene.get_dirty_rects(), [rect1, rect2])

        scene.clear_dirty_rects()
        self.assertEqual(scene.get_dirty_rects(), [rect1, rect2]) # Previous frame\"s dirty rects are still there
        scene.add_dirty_rect(rect3)
        self.assertEqual(scene.get_dirty_rects(), [rect1, rect2, rect3])

        scene.clear_dirty_rects()
        self.assertEqual(scene.get_dirty_rects(), [rect3]) # Only current frame\"s dirty rects are cleared

    @patch.object(BaseScene, 'render')
    def test_interface_calls_display_update_with_dirty_rects(self, mock_scene_render):
        interface = Interface("Test Game", (800, 600))
        scene = BaseScene()
        interface.set_scene("test_scene", scene)

        # Simulate scene rendering returning dirty rects
        mock_rect1 = MockRect() # Use MockRect directly
        mock_rect2 = MockRect() # Use MockRect directly
        scene.add_dirty_rect(mock_rect1)
        scene.add_dirty_rect(mock_rect2)

        interface.render()

        mock_scene_render.assert_called_once_with(interface.screen)
        pygame.display.update.assert_called_once_with([mock_rect1, mock_rect2])

    def test_entity_render_returns_rects(self):
        entity = Entity(0, 0)
        renderer = RectangleRenderer(10, 10, (255, 0, 0))
        entity.add_component(renderer)

        rendered_rects = entity.render(self.mock_screen)
        self.assertIsInstance(rendered_rects, list)
        self.assertEqual(len(rendered_rects), 1)
        self.assertIsInstance(rendered_rects[0], MockRect) # Check for MockRect

    def test_rectangle_renderer_render_returns_rect(self):
        entity = Entity(0, 0)
        renderer = RectangleRenderer(10, 10, (255, 0, 0))
        renderer.attach(entity)

        returned_rect = renderer.render(self.mock_screen)
        self.assertIsInstance(returned_rect, MockRect) # Mocked pygame.Rect
        self.assertEqual(returned_rect.x, -5)
        self.assertEqual(returned_rect.y, -5)
        self.assertEqual(returned_rect.w, 10)
        self.assertEqual(returned_rect.h, 10)

    def test_sprite_render_returns_rect(self):
        sprite = Sprite(0, 0)
        # Mock image and rect for the sprite
        mock_image = MockSurface() # Use our custom mock surface
        mock_image.get_rect.return_value = MockRect(w=50, h=50) # Initial position doesn\'t matter for get_rect
        sprite.image = mock_image
        sprite.rect = mock_image.get_rect()
        sprite.position = pygame.math.Vector2(0, 0) # Ensure sprite position is (0,0)

        returned_rect = sprite.render(self.mock_screen)
        self.assertIsInstance(returned_rect, MockRect) # Mocked pygame.Rect
        self.assertEqual(returned_rect.x, -25)
        self.assertEqual(returned_rect.y, -25)
        self.assertEqual(returned_rect.w, 50)
        self.assertEqual(returned_rect.h, 50)

if __name__ == '__main__':
    unittest.main()

