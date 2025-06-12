from .core.interface import Interface
from .core.entity import Entity
from .core.sprite import Sprite
from .core.camera import Camera
from .core.advanced_camera import AdvancedCamera
from .core.input import input_manager
from .core.component import Component
from .core.components.keyboard_controller import KeyboardController
from .core.components.gamepad_controller import GamepadController
from .core.components.rectangle_renderer import RectangleRenderer
from .core.components.collider import Collider
from .core.components.physics import Physics
from .core.components.particle_system import ParticleSystem
from .core.components.tilemap import TileMap
from .core.components.network_component import NetworkComponent
from .multiplayer import DedicatedServer, Client, SyncComponent
from .core.scenes.base_scene import BaseScene
from .core.save_manager import SaveManager
from .core.pathfinding import astar
import multiprocessing as mp

class Engine:
    def __init__(self, title: str = "PyEngine Game", width: int = 800, height: int = 600, num_threads: int = None):
        # Create interface with title and size
        self.interface = Interface(title, (width, height))
        self.camera = Camera(width, height)
        self.input = input_manager
        
        # Set number of threads
        self.num_threads = num_threads if num_threads is not None else mp.cpu_count()

    def set_scene(self, name: str, scene):
        """Add and set a scene as the current scene"""
        self.interface.set_scene(name, scene)

    def add_scene(self, name: str, scene):
        """Add a scene to the engine"""
        self.interface.add_scene(name, scene)

    def change_scene(self, name: str):
        """Change to a different scene"""
        self.interface.change_scene(name)

    def set_num_threads(self, num_threads: int):
        """Set the number of threads for parallel processing"""
        self.num_threads = max(1, num_threads)  # Ensure at least 1 thread
        current_scene = self.interface.get_current_scene()
        if current_scene:
            current_scene.set_num_threads(self.num_threads)

    def run(self):
        """Start the game loop"""
        self.interface.run()

# Convenience function to create and start the engine
def create_engine(title: str = "PyEngine Game", width: int = 800, height: int = 600, 
                 num_threads: int = None) -> Engine:
    return Engine(title, width, height, num_threads)

# Add UI components to exports
from .core.components.ui.button import Button
from .core.components.ui.label import Label
from .core.components.ui.panel import Panel
from .core.components.ui.progress_bar import ProgressBar
from .core.components.ui.input import Input
from .core.components.ui.select import Select
from .core.components.ui.input_select import InputSelect
from .core.components.ui.radio_button import RadioGroup
from .core.components.ui.html_view import HTMLView
from .core.components.ui.slider import Slider
from .core.components.ui.toggle import Toggle
from .core.components.ui.tooltip import TooltipMixin
from .core.components.ui.modal import Modal, MessageBox, ConfirmDialog
from .core.components.ui.tabs import Tabs
from .core.components.ui.menu import Menu, MenuItem
from .core.components.ui.grid import Grid, GridColumn
from .core.components.ui.image import Image, Icon
from .core.components.ui.scrollview import ScrollView
from .core.components.ui.titled_panel import TitledPanel
from .core.components.ui.checkbox import Checkbox
from .core.components.ui.circular_progress import CircularProgress

__all__ = [
    # Core components
    'Engine',
    'Interface',
    'BaseScene',
    'Entity',
    'Sprite',
    'Camera',
    'AdvancedCamera',
    'input_manager',
    'create_engine',
    'Component',
    'KeyboardController',
    'GamepadController',
    'RectangleRenderer',
    'Collider',
    'Physics',
    'ParticleSystem',
    'TileMap',
    'NetworkComponent',
    'DedicatedServer',
    'Client',
    'SyncComponent',
    'SaveManager',
    'astar',
    
    # UI components
    'Button',
    'Label',
    'Panel',
    'ProgressBar',
    'Input',
    'Select',
    'InputSelect',
    'RadioGroup',
    'HTMLView',
    'Slider',
    'Toggle',
    'TooltipMixin',
    'Modal',
    'MessageBox',
    'ConfirmDialog',
    'Tabs',
    'Menu',
    'MenuItem',
    'Grid',
    'GridColumn',
    'Image',
    'Icon',
    'ScrollView',
    'TitledPanel',
    'Checkbox',
    'CircularProgress'
]


from .core.components.state_machine_component import StateMachineComponent
from .core.components.timer_component import TimerComponent

__all__.extend([
    'StateMachineComponent',
    'TimerComponent'
])



from .core.components.health_component import HealthComponent
from .core.components.inventory_component import InventoryComponent

__all__.extend([
    'HealthComponent',
    'InventoryComponent'
])

