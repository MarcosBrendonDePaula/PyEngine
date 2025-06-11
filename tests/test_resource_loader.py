import unittest
from unittest.mock import MagicMock, patch
import pygame
import os

# Mock pygame for testing purposes
pygame.init = MagicMock()
pygame.font = MagicMock()
pygame.display = MagicMock()
pygame.Surface = MagicMock()
pygame.Rect = MagicMock(return_value=MagicMock())
pygame.image = MagicMock()
pygame.mixer = MagicMock()

# Mock the convert and convert_alpha methods for pygame.Surface
# They should return a mock object to simulate a converted surface
def mock_convert():
    mock_surface = MagicMock()
    mock_surface.get_rect.return_value = MagicMock()
    return mock_surface

def mock_convert_alpha():
    mock_surface = MagicMock()
    mock_surface.get_rect.return_value = MagicMock()
    return mock_surface

pygame.Surface.return_value.convert = MagicMock(side_effect=mock_convert)
pygame.Surface.return_value.convert_alpha = MagicMock(side_effect=mock_convert_alpha)

# Import the class to be tested after mocking pygame
from engine.core.resource_loader import ResourceLoader

class TestResourceLoader(unittest.TestCase):

    def setUp(self):
        # Reset the singleton instance before each test
        ResourceLoader._instance = None
        self.loader = ResourceLoader()
        self.test_dir = "./test_resources"
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        # Clean up created test files and directory
        if os.path.exists(os.path.join(self.test_dir, "test_image.png")):
            os.remove(os.path.join(self.test_dir, "test_image.png"))
        if os.path.exists(os.path.join(self.test_dir, "test_image.jpg")):
            os.remove(os.path.join(self.test_dir, "test_image.jpg"))
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    @patch('pygame.image.load')
    def test_load_png_converts_alpha(self, mock_pygame_image_load):
        # Create a dummy file for os.path.exists to return True
        with open(os.path.join(self.test_dir, "test_image.png"), "w") as f:
            f.write("dummy png content")

        mock_surface = MagicMock()
        mock_surface.convert_alpha.return_value = mock_surface # Simulate conversion
        mock_pygame_image_load.return_value = mock_surface

        resource_path = os.path.join(self.test_dir, "test_image.png")
        loaded_resource = self.loader.load_resource(resource_path)

        mock_pygame_image_load.assert_called_once_with(resource_path)
        mock_surface.convert_alpha.assert_called_once()
        self.assertEqual(loaded_resource, mock_surface)

    @patch('pygame.image.load')
    def test_load_jpg_converts(self, mock_pygame_image_load):
        # Create a dummy file for os.path.exists to return True
        with open(os.path.join(self.test_dir, "test_image.jpg"), "w") as f:
            f.write("dummy jpg content")

        mock_surface = MagicMock()
        mock_surface.convert.return_value = mock_surface # Simulate conversion
        mock_pygame_image_load.return_value = mock_surface

        resource_path = os.path.join(self.test_dir, "test_image.jpg")
        loaded_resource = self.loader.load_resource(resource_path)

        mock_pygame_image_load.assert_called_once_with(resource_path)
        mock_surface.convert.assert_called_once()
        self.assertEqual(loaded_resource, mock_surface)

    @patch('pygame.mixer.Sound')
    def test_load_wav_sound(self, mock_pygame_mixer_sound):
        with open(os.path.join(self.test_dir, "test_sound.wav"), "w") as f:
            f.write("dummy wav content")
        
        mock_sound = MagicMock()
        mock_pygame_mixer_sound.return_value = mock_sound

        resource_path = os.path.join(self.test_dir, "test_sound.wav")
        loaded_resource = self.loader.load_resource(resource_path)

        mock_pygame_mixer_sound.assert_called_once_with(resource_path)
        self.assertEqual(loaded_resource, mock_sound)

    def test_resource_caching(self):
        # Create a dummy file for os.path.exists to return True
        with open(os.path.join(self.test_dir, "test_image.png"), "w") as f:
            f.write("dummy png content")

        resource_path = os.path.join(self.test_dir, "test_image.png")
        
        # Load resource first time
        loaded_resource_1 = self.loader.load_resource(resource_path, resource_id="img1")
        
        # Load resource second time, should be from cache
        loaded_resource_2 = self.loader.load_resource(resource_path, resource_id="img1")

        self.assertEqual(loaded_resource_1, loaded_resource_2)
        self.assertEqual(self.loader._reference_count["img1"], 2)

    def test_unload_resource(self):
        with open(os.path.join(self.test_dir, "test_image.png"), "w") as f:
            f.write("dummy png content")

        resource_path = os.path.join(self.test_dir, "test_image.png")
        self.loader.load_resource(resource_path, resource_id="img1")
        self.loader.unload_resource("img1")
        self.assertNotIn("img1", self.loader._resources)
        self.assertNotIn("img1", self.loader._reference_count)

    def test_unload_resource_multiple_references(self):
        with open(os.path.join(self.test_dir, "test_image.png"), "w") as f:
            f.write("dummy png content")

        resource_path = os.path.join(self.test_dir, "test_image.png")
        self.loader.load_resource(resource_path, resource_id="img1")
        self.loader.load_resource(resource_path, resource_id="img1")
        self.loader.unload_resource("img1")
        self.assertIn("img1", self.loader._resources)
        self.assertEqual(self.loader._reference_count["img1"], 1)
        self.loader.unload_resource("img1")
        self.assertNotIn("img1", self.loader._resources)

    def test_load_non_existent_resource(self):
        resource_path = os.path.join(self.test_dir, "non_existent.png")
        loaded_resource = self.loader.load_resource(resource_path)
        self.assertIsNone(loaded_resource)

if __name__ == '__main__':
    unittest.main()

