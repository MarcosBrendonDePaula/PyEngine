import unittest
from unittest.mock import MagicMock, patch
import pygame
import os

# Mock pygame for testing purposes
pygame.init = MagicMock()
pygame.font.init = MagicMock()
pygame.display = MagicMock()
pygame.display.update = MagicMock()
pygame.display.flip = MagicMock()

# Mock pygame.Rect to return a mock object with expected attributes
pygame.Rect = MagicMock(return_value=MagicMock(x=0, y=0, w=0, h=0, colliderect=MagicMock(return_value=True)))

# Mock pygame.image.load
pygame.image = MagicMock()
pygame.image.load = MagicMock()

# Mock pygame.mixer.Sound as a class
pygame.mixer = MagicMock()
pygame.mixer.Sound = MagicMock() # Mock as a class, not an instance

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
        return MagicMock(x=0, y=0, w=0, h=0) # Return a mock rect

pygame.Surface = MockSurface # Assign our custom mock class to pygame.Surface

# Mock pygame.draw
pygame.draw = MagicMock()
pygame.draw.rect = MagicMock() 

# Import the class to be tested after mocking pygame
from engine.core.resource_loader import ResourceLoader

class TestResourceLoader(unittest.TestCase):

    def setUp(self):
        # Reset the singleton instance before each test
        ResourceLoader._instance = None
        self.loader = ResourceLoader()

    def test_load_png_converts_alpha(self):
        with patch("os.path.exists", return_value=True):
            with patch("pygame.image.load") as mock_pygame_image_load:
                mock_surface_instance = MockSurface() # Use our custom mock surface
                mock_pygame_image_load.return_value = mock_surface_instance

                resource_path = "path/to/image.png"
                loaded_resource = self.loader.load_resource(resource_path)

                mock_pygame_image_load.assert_called_once_with(resource_path)
                mock_surface_instance.convert_alpha.assert_called_once()
                self.assertEqual(loaded_resource, mock_surface_instance)

    def test_load_jpg_converts(self):
        with patch("os.path.exists", return_value=True):
            with patch("pygame.image.load") as mock_pygame_image_load:
                mock_surface_instance = MockSurface() # Use our custom mock surface
                mock_pygame_image_load.return_value = mock_surface_instance

                resource_path = "path/to/image.jpg"
                loaded_resource = self.loader.load_resource(resource_path)

                mock_pygame_image_load.assert_called_once_with(resource_path)
                mock_surface_instance.convert.assert_called_once()
                self.assertEqual(loaded_resource, mock_surface_instance)

    def test_load_wav_sound(self):
        with patch("os.path.exists", return_value=True):
            with patch("pygame.mixer.Sound") as mock_pygame_mixer_sound:
                mock_sound_instance = MagicMock()
                mock_pygame_mixer_sound.return_value = mock_sound_instance

                resource_path = "path/to/sound.wav"
                loaded_resource = self.loader.load_resource(resource_path)

                mock_pygame_mixer_sound.assert_called_once_with(resource_path)
                self.assertEqual(loaded_resource, mock_sound_instance)

    def test_resource_caching(self):
        with patch("os.path.exists", return_value=True):
            with patch("pygame.image.load") as mock_pygame_image_load:
                mock_surface_instance = MockSurface()
                mock_pygame_image_load.return_value = mock_surface_instance

                loaded_resource_1 = self.loader.load_resource("path/to/image.png", resource_id="img1")
                loaded_resource_2 = self.loader.load_resource("path/to/image.png", resource_id="img1")

                self.assertEqual(loaded_resource_1, loaded_resource_2)
                self.assertEqual(self.loader._reference_count["img1"], 2)

    def test_unload_resource(self):
        with patch("os.path.exists", return_value=True):
            with patch("pygame.image.load") as mock_pygame_image_load:
                mock_surface_instance = MockSurface()
                mock_pygame_image_load.return_value = mock_surface_instance
                self.loader.load_resource("path/to/image.png", resource_id="img1")
        self.loader.unload_resource("img1")
        self.assertNotIn("img1", self.loader._resources)
        self.assertNotIn("img1", self.loader._reference_count)

    def test_unload_resource_multiple_references(self):
        with patch("os.path.exists", return_value=True):
            with patch("pygame.image.load") as mock_pygame_image_load:
                mock_surface_instance = MockSurface()
                mock_pygame_image_load.return_value = mock_surface_instance
                self.loader.load_resource("path/to/image.png", resource_id="img1")
                self.loader.load_resource("path/to/image.png", resource_id="img1")
        self.loader.unload_resource("img1")
        self.assertIn("img1", self.loader._resources)
        self.assertEqual(self.loader._reference_count["img1"], 1)
        self.loader.unload_resource("img1")
        self.assertNotIn("img1", self.loader._resources)

    def test_load_non_existent_resource(self):
        with patch("os.path.exists", return_value=False):
            loaded_resource = self.loader.load_resource("non_existent.png")
            self.assertIsNone(loaded_resource)

if __name__ == '__main__':
    unittest.main()

