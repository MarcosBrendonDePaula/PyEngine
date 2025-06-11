import unittest
import pygame

from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity

class DummyInterface:
    def __init__(self, size=(100, 100)):
        self.size = size

class TestEntity(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.ticks = 0

    def get_rect(self):
        return pygame.Rect(self.position.x, self.position.y, 10, 10)

    def tick(self):
        self.ticks += 1

class BaseSceneVisibilityTests(unittest.TestCase):
    def setUp(self):
        self.scene = BaseScene()
        self.scene.set_interface(DummyInterface())
        self.scene._is_loaded = True

    def test_is_entity_visible(self):
        inside = TestEntity(10, 10)
        outside = TestEntity(200, 200)
        self.assertTrue(self.scene.is_entity_visible(inside, margin=0))
        self.assertFalse(self.scene.is_entity_visible(outside, margin=0))
        self.assertTrue(self.scene.is_entity_visible(outside, margin=150))

    def test_update_skips_offscreen_entities(self):
        visible = TestEntity(20, 20)
        offscreen = TestEntity(150, 150)
        self.scene.culling_margin = 0
        self.scene.add_entity(visible)
        self.scene.add_entity(offscreen)
        self.scene.update()
        self.assertEqual(visible.ticks, 1)
        self.assertEqual(offscreen.ticks, 0)

    def test_set_culling_margin(self):
        self.scene.set_culling_margin(-50)
        self.assertEqual(self.scene.culling_margin, 0)
        self.scene.set_culling_margin(30)
        self.assertEqual(self.scene.culling_margin, 30)

if __name__ == '__main__':
    unittest.main()
