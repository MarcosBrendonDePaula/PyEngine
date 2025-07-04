"""
Tests for the threading system in PyEngine.
"""

import unittest
import time
import threading
from unittest.mock import Mock, patch

from engine.core.thread_pool import ThreadPool, ThreadSafeCounter, get_global_thread_pool
from engine.core.entity import Entity
from engine.core.component import Component
from engine.core.scenes.base_scene import BaseScene, ThreadConfig

class SimpleComponent(Component):
    """Simple test component."""
    
    def __init__(self):
        super().__init__()
        self.update_count = 0
        self.last_delta_time = 0.0
        
    def update(self):
        self.update_count += 1
        if self.entity:
            self.last_delta_time = self.entity.delta_time

class TestThreadPool(unittest.TestCase):
    """Test the ThreadPool class."""
    
    def setUp(self):
        self.thread_pool = ThreadPool(max_workers=4)
        
    def tearDown(self):
        self.thread_pool.shutdown()
        
    def test_thread_pool_creation(self):
        """Test that thread pool is created correctly."""
        self.assertEqual(self.thread_pool.max_workers, 4)
        self.assertIsNotNone(self.thread_pool.executor)
        
    def test_sequential_update_small_batch(self):
        """Test that small batches use sequential processing."""
        entities = []
        for i in range(5):  # Small batch
            entity = Entity()
            entity.delta_time = 0.016
            component = SimpleComponent()
            entity.add_component(component)
            entities.append(entity)
            
        # This should use sequential processing due to small batch size
        self.thread_pool.update_entities_parallel(entities, 0.016, min_batch_size=10)
        
        # Verify all components were updated
        for entity in entities:
            component = entity.get_component(SimpleComponent)
            self.assertEqual(component.update_count, 1)
            self.assertEqual(component.last_delta_time, 0.016)
            
    def test_parallel_update_large_batch(self):
        """Test that large batches use parallel processing."""
        entities = []
        for i in range(50):  # Large batch
            entity = Entity()
            entity.delta_time = 0.016
            component = SimpleComponent()
            entity.add_component(component)
            entities.append(entity)
            
        start_time = time.time()
        self.thread_pool.update_entities_parallel(entities, 0.016, min_batch_size=10)
        end_time = time.time()
        
        # Verify all components were updated
        for entity in entities:
            component = entity.get_component(SimpleComponent)
            self.assertEqual(component.update_count, 1)
            self.assertEqual(component.last_delta_time, 0.016)
            
        # Should complete reasonably quickly
        self.assertLess(end_time - start_time, 1.0)

class TestThreadSafeCounter(unittest.TestCase):
    """Test the ThreadSafeCounter class."""
    
    def test_counter_operations(self):
        """Test basic counter operations."""
        counter = ThreadSafeCounter()
        
        self.assertEqual(counter.value, 0)
        
        self.assertEqual(counter.increment(), 1)
        self.assertEqual(counter.increment(5), 6)
        self.assertEqual(counter.decrement(2), 4)
        
        counter.reset()
        self.assertEqual(counter.value, 0)
        
    def test_thread_safety(self):
        """Test that counter is thread-safe."""
        counter = ThreadSafeCounter()
        num_threads = 10
        increments_per_thread = 100
        
        def increment_worker():
            for _ in range(increments_per_thread):
                counter.increment()
                
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=increment_worker)
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
            
        expected_value = num_threads * increments_per_thread
        self.assertEqual(counter.value, expected_value)

class TestEntityThreadSafety(unittest.TestCase):
    """Test entity thread safety."""
    
    def test_component_operations_thread_safe(self):
        """Test that component operations are thread-safe."""
        entity = Entity()
        
        def add_components():
            for i in range(10):
                try:
                    component = SimpleComponent()
                    # Use a unique class for each component to avoid conflicts
                    component.__class__ = type(f'SimpleComponent{i}', (SimpleComponent,), {})
                    entity.add_component(component)
                except ValueError:
                    # Expected when trying to add duplicate component types
                    pass
                    
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=add_components)
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
            
        # Should have some components added without crashes
        self.assertGreaterEqual(len(entity.components), 1)
        
    def test_update_thread_safety(self):
        """Test that entity updates are thread-safe."""
        entity = Entity()
        entity.delta_time = 0.016
        
        component = SimpleComponent()
        entity.add_component(component)
        
        def update_worker():
            for _ in range(100):
                entity.update()
                time.sleep(0.001)  # Small delay to increase chance of race conditions
                
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=update_worker)
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
            
        # Should have been updated many times without crashes
        self.assertGreater(component.update_count, 100)

class TestBaseSceneThreading(unittest.TestCase):
    """Test BaseScene threading functionality."""
    
    def test_thread_config(self):
        """Test thread configuration."""
        config = ThreadConfig(
            enabled=True,
            max_workers=8,
            min_entities_for_threading=15,
            use_global_pool=False
        )
        
        scene = BaseScene(thread_config=config)
        self.assertEqual(scene.get_thread_config(), config)
        
    def test_threading_enable_disable(self):
        """Test enabling and disabling threading."""
        scene = BaseScene()
        
        # Should start with threading enabled by default
        self.assertTrue(scene._thread_config.enabled)
        
        scene.disable_threading()
        self.assertFalse(scene._thread_config.enabled)
        
        scene.enable_threading()
        self.assertTrue(scene._thread_config.enabled)
        
    def test_entity_update_with_threading(self):
        """Test entity updates with threading enabled."""
        scene = BaseScene()
        entities = []
        
        # Create enough entities to trigger threading
        for i in range(30):
            entity = Entity()
            component = SimpleComponent()
            entity.add_component(component)
            entities.append(entity)
            scene.add_entity(entity)
            
        # Update scene
        scene.update(0.016)
        
        # Verify all entities were updated
        for entity in entities:
            component = entity.get_component(SimpleComponent)
            self.assertEqual(component.update_count, 1)
            
    def test_entity_update_without_threading(self):
        """Test entity updates with threading disabled."""
        scene = BaseScene()
        scene.disable_threading()
        entities = []
        
        # Create entities
        for i in range(30):
            entity = Entity()
            component = SimpleComponent()
            entity.add_component(component)
            entities.append(entity)
            scene.add_entity(entity)
            
        # Update scene
        scene.update(0.016)
        
        # Verify all entities were updated
        for entity in entities:
            component = entity.get_component(SimpleComponent)
            self.assertEqual(component.update_count, 1)

if __name__ == '__main__':
    # Run with minimal output due to threading complexity
    unittest.main(verbosity=1)