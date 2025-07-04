"""PyEngine public API."""

__version__ = "0.1.0"

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
from .core.scenes.base_scene import BaseScene, ThreadConfig
from .core.thread_pool import ThreadPool, get_global_thread_pool, shutdown_global_thread_pool
from .core.save_manager import SaveManager
from .core.pathfinding import astar
import multiprocessing as mp

class Engine:
    ENGINE_INSTANCE = None 
    def __init__(self, title: str = "PyEngine Game", width: int = 800, height: int = 600, 
                 num_threads: int = None, enable_threading: bool = True):
        # Create interface with title and size
        self.interface = Interface(title, (width, height))
        self.camera = Camera(width, height)
        self.input = input_manager
        
        # Set number of threads
        self.num_threads = num_threads if num_threads is not None else min(mp.cpu_count(), 8)
        self.threading_enabled = enable_threading
        
        # Initialize global thread pool if threading is enabled
        if self.threading_enabled:
            self.thread_pool = get_global_thread_pool()
        else:
            self.thread_pool = None
            
        Engine.ENGINE_INSTANCE = self
        print(f"Engine initialized with {self.num_threads} threads, threading {'enabled' if enable_threading else 'disabled'}")

    def set_scene(self, name: str, scene):
        """Add and set a scene as the current scene"""
        # Configure scene threading if not already configured
        if hasattr(scene, '_thread_config') and scene._thread_config.enabled != self.threading_enabled:
            thread_config = ThreadConfig(
                enabled=self.threading_enabled,
                max_workers=self.num_threads,
                use_global_pool=True
            )
            scene.configure_threading(thread_config)
        self.interface.set_scene(name, scene)

    def add_scene(self, name: str, scene):
        """Add a scene to the engine"""
        # Configure scene threading
        if hasattr(scene, '_thread_config'):
            thread_config = ThreadConfig(
                enabled=self.threading_enabled,
                max_workers=self.num_threads,
                use_global_pool=True
            )
            scene.configure_threading(thread_config)
        self.interface.add_scene(name, scene)

    def change_scene(self, name: str):
        """Change to a different scene"""
        self.interface.change_scene(name)

    def set_num_threads(self, num_threads: int):
        """Set the number of threads for parallel processing"""
        self.num_threads = max(1, num_threads)  # Ensure at least 1 thread
        
        # Update all scenes in scene manager
        if hasattr(self.interface.scene_manager, '_scenes'):
            for scene in self.interface.scene_manager._scenes.values():
                if hasattr(scene, 'set_thread_count'):
                    scene.set_thread_count(self.num_threads)
                    
    def enable_threading(self, enabled: bool = True):
        """Enable or disable threading for all scenes"""
        self.threading_enabled = enabled
        
        # Update all scenes
        if hasattr(self.interface.scene_manager, '_scenes'):
            for scene in self.interface.scene_manager._scenes.values():
                if hasattr(scene, 'enable_threading'):
                    scene.enable_threading(enabled)
                    
        # Initialize or shutdown global thread pool
        if enabled and self.thread_pool is None:
            self.thread_pool = get_global_thread_pool()
        elif not enabled and self.thread_pool is not None:
            # Don't shutdown global pool, just stop using it
            self.thread_pool = None

    def run(self):
        """Start the game loop"""
        try:
            self.interface.run()
        finally:
            # Cleanup threading resources
            if self.threading_enabled:
                shutdown_global_thread_pool()
                
    def shutdown(self):
        """Shutdown the engine and cleanup resources"""
        if self.threading_enabled:
            shutdown_global_thread_pool()
        print("Engine shutdown complete")

# Convenience function to create and start the engine
def create_engine(title: str = "PyEngine Game", width: int = 800, height: int = 600, 
                 num_threads: int = None) -> Engine:
    """
    Create a PyEngine instance with automatic threading configuration.
    
    Args:
        title: Window title
        width: Window width
        height: Window height
        num_threads: Number of threads to use. If None, auto-detects optimal count.
    
    Returns:
        Configured Engine instance
    """
    # Auto-detect optimal thread count if not specified
    if num_threads is None:
        import multiprocessing as mp
        cpu_count = mp.cpu_count()
        num_threads = max(1, int(cpu_count * 0.75))  # Use 75% of available cores
    
    # Enable threading if more than 1 thread requested
    enable_threading = num_threads > 1
    
    return Engine(title, width, height, num_threads, enable_threading)

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
    'ThreadConfig',
    'ThreadPool',
    'get_global_thread_pool',
    'shutdown_global_thread_pool',
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
    'TitledPanel'
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

