import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Callable, Any, Optional
import time

class ThreadPool:
    """Thread pool for parallel entity updates with optimized batching."""
    
    def __init__(self, max_workers: Optional[int] = None):
        """
        Initialize thread pool.
        
        Args:
            max_workers: Maximum number of worker threads. If None, uses CPU count.
        """
        import multiprocessing
        self.max_workers = max_workers or min(multiprocessing.cpu_count(), 8)  # Cap at 8 for efficiency
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self._lock = threading.RLock()  # Reentrant lock for nested operations
        
    def update_entities_parallel(self, entities: List, delta_time: float, 
                                min_batch_size: int = 10) -> None:
        """
        Update entities in parallel using optimal batching.
        
        Args:
            entities: List of entities to update
            delta_time: Time delta for this frame
            min_batch_size: Minimum entities per batch to justify threading overhead
        """
        if not entities:
            return
            
        # For small entity counts, use sequential processing to avoid thread overhead
        if len(entities) < min_batch_size:
            self._update_entities_sequential(entities, delta_time)
            return
            
        # Calculate optimal batch size based on entity count and thread count
        batch_size = max(min_batch_size, len(entities) // self.max_workers)
        batches = self._create_batches(entities, batch_size)
        
        if len(batches) == 1:
            # Single batch, process sequentially
            self._update_entities_sequential(entities, delta_time)
            return
            
        # Process batches in parallel
        futures = []
        for batch in batches:
            future = self.executor.submit(self._update_batch, batch, delta_time)
            futures.append(future)
            
        # Wait for all batches to complete
        for future in as_completed(futures):
            try:
                future.result()  # This will raise any exceptions that occurred
            except Exception as e:
                print(f"Error in parallel entity update: {e}")
                
    def _create_batches(self, entities: List, batch_size: int) -> List[List]:
        """Create batches of entities for parallel processing."""
        batches = []
        for i in range(0, len(entities), batch_size):
            batch = entities[i:i + batch_size]
            batches.append(batch)
        return batches
        
    def _update_batch(self, entities: List, delta_time: float) -> None:
        """Update a batch of entities."""
        for entity in entities:
            if entity.active:
                try:
                    entity.delta_time = delta_time
                    entity.update()
                except Exception as e:
                    print(f"Error updating entity {entity.id}: {e}")
                    
    def _update_entities_sequential(self, entities: List, delta_time: float) -> None:
        """Update entities sequentially (fallback for small batches)."""
        for entity in entities:
            if entity.active:
                try:
                    entity.delta_time = delta_time
                    entity.update()
                except Exception as e:
                    print(f"Error updating entity {entity.id}: {e}")
                    
    def execute_parallel(self, func: Callable, items: List, *args, **kwargs) -> List[Any]:
        """
        Execute a function in parallel over a list of items.
        
        Args:
            func: Function to execute
            items: List of items to process
            *args, **kwargs: Additional arguments for the function
            
        Returns:
            List of results from function execution
        """
        if not items:
            return []
            
        futures = []
        for item in items:
            future = self.executor.submit(func, item, *args, **kwargs)
            futures.append(future)
            
        results = []
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"Error in parallel execution: {e}")
                results.append(None)
                
        return results
        
    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the thread pool."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=wait)
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

class ThreadSafeCounter:
    """Thread-safe counter for tracking operations across threads."""
    
    def __init__(self, initial_value: int = 0):
        self._value = initial_value
        self._lock = threading.Lock()
        
    def increment(self, amount: int = 1) -> int:
        with self._lock:
            self._value += amount
            return self._value
            
    def decrement(self, amount: int = 1) -> int:
        with self._lock:
            self._value -= amount
            return self._value
            
    @property
    def value(self) -> int:
        with self._lock:
            return self._value
            
    def reset(self) -> None:
        with self._lock:
            self._value = 0

# Global thread pool instance for the engine
_global_thread_pool: Optional[ThreadPool] = None

def get_global_thread_pool() -> ThreadPool:
    """Get or create the global thread pool instance."""
    global _global_thread_pool
    if _global_thread_pool is None:
        _global_thread_pool = ThreadPool()
    return _global_thread_pool

def shutdown_global_thread_pool() -> None:
    """Shutdown the global thread pool."""
    global _global_thread_pool
    if _global_thread_pool is not None:
        _global_thread_pool.shutdown()
        _global_thread_pool = None