import pygame
import os
import time
import threading
import queue
from typing import Dict, List, Tuple, Optional, Any, Callable, Set, Union
import weakref

class ResourceCache:
    """
    A cache for resources with memory management and transformation caching.
    """
    def __init__(self, max_memory_mb: int = 512):
        self.resources: Dict[str, Any] = {}
        self.reference_counts: Dict[str, int] = {}
        self.last_accessed: Dict[str, float] = {}
        self.resource_sizes: Dict[str, int] = {}
        self.transformed_resources: Dict[str, Dict[str, Any]] = {}
        self.max_memory = max_memory_mb * 1024 * 1024  # Convert to bytes
        self.current_memory = 0
        self.lock = threading.RLock()  # Reentrant lock for thread safety
    
    def add(self, key: str, resource: Any) -> None:
        """Add a resource to the cache."""
        with self.lock:
            if key in self.resources:
                self.reference_counts[key] += 1
            else:
                self.resources[key] = resource
                self.reference_counts[key] = 1
                self.transformed_resources[key] = {}
                
                # Estimate resource size
                size = self._estimate_resource_size(resource)
                self.resource_sizes[key] = size
                self.current_memory += size
                
            self.last_accessed[key] = time.time()
            
            # Check if we need to free memory
            self._manage_memory()
    
    def get(self, key: str) -> Optional[Any]:
        """Get a resource from the cache."""
        with self.lock:
            if key in self.resources:
                self.last_accessed[key] = time.time()
                return self.resources[key]
            return None
    
    def get_transformed(self, key: str, transform_key: str) -> Optional[Any]:
        """Get a transformed version of a resource."""
        with self.lock:
            if key in self.transformed_resources and transform_key in self.transformed_resources[key]:
                self.last_accessed[key] = time.time()
                return self.transformed_resources[key][transform_key]
            return None
    
    def add_transformed(self, key: str, transform_key: str, resource: Any) -> None:
        """Add a transformed version of a resource to the cache."""
        with self.lock:
            if key in self.transformed_resources:
                self.transformed_resources[key][transform_key] = resource
                
                # Estimate and track the size of the transformed resource
                size = self._estimate_resource_size(resource)
                self.current_memory += size
                
                # Check if we need to free memory
                self._manage_memory()
    
    def remove(self, key: str) -> None:
        """Remove a resource from the cache."""
        with self.lock:
            if key in self.resources:
                self.reference_counts[key] -= 1
                
                if self.reference_counts[key] <= 0:
                    # Free memory
                    self.current_memory -= self.resource_sizes.get(key, 0)
                    
                    # Free transformed resources
                    for transformed in self.transformed_resources.get(key, {}).values():
                        self.current_memory -= self._estimate_resource_size(transformed)
                    
                    # Remove from dictionaries
                    del self.resources[key]
                    del self.reference_counts[key]
                    del self.last_accessed[key]
                    del self.resource_sizes[key]
                    del self.transformed_resources[key]
    
    def clear(self) -> None:
        """Clear all resources from the cache."""
        with self.lock:
            self.resources.clear()
            self.reference_counts.clear()
            self.last_accessed.clear()
            self.resource_sizes.clear()
            self.transformed_resources.clear()
            self.current_memory = 0
    
    def _manage_memory(self) -> None:
        """Free memory if we're over the limit."""
        if self.current_memory <= self.max_memory:
            return
            
        # Get resources that can be freed (reference count = 0)
        candidates = []
        for key, count in self.reference_counts.items():
            if count <= 0:
                candidates.append((key, self.last_accessed.get(key, 0)))
        
        # Sort by last accessed time (oldest first)
        candidates.sort(key=lambda x: x[1])
        
        # Free resources until we're under the limit
        for key, _ in candidates:
            if self.current_memory <= self.max_memory:
                break
                
            # Free memory
            self.current_memory -= self.resource_sizes.get(key, 0)
            
            # Free transformed resources
            for transformed in self.transformed_resources.get(key, {}).values():
                self.current_memory -= self._estimate_resource_size(transformed)
            
            # Remove from dictionaries
            del self.resources[key]
            del self.reference_counts[key]
            del self.last_accessed[key]
            del self.resource_sizes[key]
            del self.transformed_resources[key]
    
    def _estimate_resource_size(self, resource: Any) -> int:
        """Estimate the memory size of a resource in bytes."""
        if isinstance(resource, pygame.Surface):
            width, height = resource.get_size()
            if resource.get_bitsize() == 32:  # RGBA
                bytes_per_pixel = 4
            else:  # RGB
                bytes_per_pixel = 3
            return width * height * bytes_per_pixel
        elif isinstance(resource, pygame.mixer.Sound):
            # Rough estimate based on typical sound file sizes
            return 1024 * 1024  # 1MB default for sounds
        else:
            # Default size for unknown types
            return 1024  # 1KB default
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the cache."""
        with self.lock:
            return {
                'total_resources': len(self.resources),
                'memory_usage_mb': self.current_memory / (1024 * 1024),
                'max_memory_mb': self.max_memory / (1024 * 1024),
                'resources': {
                    key: {
                        'type': type(res).__name__,
                        'ref_count': self.reference_counts[key],
                        'size_kb': self.resource_sizes[key] / 1024,
                        'transformed_count': len(self.transformed_resources[key])
                    }
                    for key, res in self.resources.items()
                }
            }


class ResourceManager:
    """
    Enhanced resource manager with advanced caching, preloading, and transformation caching.
    """
    _instance = None
    
    @classmethod
    def get_instance(cls, max_memory_mb: int = 512) -> 'ResourceManager':
        """Get the global ResourceManager instance"""
        if cls._instance is None:
            cls._instance = cls(max_memory_mb)
        return cls._instance
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ResourceManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, max_memory_mb: int = 512):
        if self._initialized:
            return
            
        self.cache = ResourceCache(max_memory_mb)
        self.loading_queue = queue.Queue()
        self.loading_thread = None
        self.loading_active = False
        self.loading_callbacks: Dict[str, List[Callable]] = {}
        self.preload_groups: Dict[str, Set[str]] = {}
        self._initialized = True
        
        print("ResourceManager initialized")
    
    def load_texture(self, path: str, resource_id: str = None, colorkey: Tuple[int, int, int] = None) -> Optional[pygame.Surface]:
        """
        Load a texture and cache it.
        
        Args:
            path: Path to the texture file
            resource_id: Optional ID for the resource (defaults to path)
            colorkey: Optional color key for transparency
            
        Returns:
            The loaded texture or None if loading failed
        """
        resource_id = resource_id or path
        
        # Check if already in cache
        texture = self.cache.get(resource_id)
        if texture:
            return texture
            
        # Load the texture
        try:
            if os.path.exists(path):
                texture = pygame.image.load(path).convert_alpha()
                
                if colorkey:
                    texture.set_colorkey(colorkey)
                
                self.cache.add(resource_id, texture)
                return texture
            else:
                print(f"Texture not found: {path}")
                return None
        except Exception as e:
            print(f"Failed to load texture {path}: {e}")
            return None
    
    def load_sound(self, path: str, resource_id: str = None) -> Optional[pygame.mixer.Sound]:
        """
        Load a sound and cache it.
        
        Args:
            path: Path to the sound file
            resource_id: Optional ID for the resource (defaults to path)
            
        Returns:
            The loaded sound or None if loading failed
        """
        resource_id = resource_id or path
        
        # Check if already in cache
        sound = self.cache.get(resource_id)
        if sound:
            return sound
            
        # Load the sound
        try:
            if os.path.exists(path):
                sound = pygame.mixer.Sound(path)
                self.cache.add(resource_id, sound)
                return sound
            else:
                print(f"Sound not found: {path}")
                return None
        except Exception as e:
            print(f"Failed to load sound {path}: {e}")
            return None
    
    def get_resource(self, resource_id: str) -> Optional[Any]:
        """Get a cached resource by its ID."""
        return self.cache.get(resource_id)
    
    def unload_resource(self, resource_id: str) -> None:
        """Decrement reference count and unload resource if no longer needed."""
        self.cache.remove(resource_id)
    
    def get_transformed_texture(self, resource_id: str, scale: Tuple[float, float] = None, 
                               flip: Tuple[bool, bool] = None, rotation: float = None, 
                               color: Tuple[int, int, int] = None) -> Optional[pygame.Surface]:
        """
        Get a transformed version of a texture, creating and caching it if needed.
        
        Args:
            resource_id: ID of the original texture
            scale: Optional (scale_x, scale_y) tuple
            flip: Optional (flip_x, flip_y) tuple
            rotation: Optional rotation angle in degrees
            color: Optional color tint
            
        Returns:
            The transformed texture or None if the original texture is not found
        """
        # Generate a transform key
        transform_key = f"s{scale}_f{flip}_r{rotation}_c{color}"
        
        # Check if the transformed version is already cached
        transformed = self.cache.get_transformed(resource_id, transform_key)
        if transformed:
            return transformed
            
        # Get the original texture
        original = self.cache.get(resource_id)
        if not original:
            return None
            
        # Apply transformations
        texture = original.copy()
        
        if scale and (scale[0] != 1.0 or scale[1] != 1.0):
            width = int(texture.get_width() * scale[0])
            height = int(texture.get_height() * scale[1])
            texture = pygame.transform.scale(texture, (width, height))
            
        if flip and (flip[0] or flip[1]):
            texture = pygame.transform.flip(texture, flip[0], flip[1])
            
        if rotation:
            texture = pygame.transform.rotate(texture, rotation)
            
        if color and color != (255, 255, 255):
            texture.fill(color, special_flags=pygame.BLEND_MULT)
            
        # Cache the transformed version
        self.cache.add_transformed(resource_id, transform_key, texture)
        
        return texture
    
    def extract_sprite_frames(self, resource_id: str, start_x: int, start_y: int, 
                             frame_width: int, frame_height: int, frame_count: int,
                             scale: Tuple[float, float] = None, flip: Tuple[bool, bool] = None,
                             colorkey: Tuple[int, int, int] = None) -> List[pygame.Surface]:
        """
        Extract and cache frames from a sprite sheet.
        
        Args:
            resource_id: ID of the sprite sheet
            start_x: Starting X position
            start_y: Starting Y position
            frame_width: Width of each frame
            frame_height: Height of each frame
            frame_count: Number of frames to extract
            scale: Optional (scale_x, scale_y) tuple
            flip: Optional (flip_x, flip_y) tuple
            colorkey: Optional color key for transparency
            
        Returns:
            List of extracted frame surfaces
        """
        # Get the sprite sheet
        sprite_sheet = self.cache.get(resource_id)
        if not sprite_sheet:
            return []
            
        frames = []
        sheet_width = sprite_sheet.get_width()
        
        for i in range(frame_count):
            x = start_x + (i * frame_width)
            if x + frame_width > sheet_width:
                break
                
            # Generate a unique ID for this frame
            frame_id = f"{resource_id}_frame_{start_x}_{start_y}_{i}_{frame_width}_{frame_height}"
            
            # Check if the frame is already cached
            frame = self.cache.get(frame_id)
            if not frame:
                # Create frame surface
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.fill((0, 0, 0, 0))
                # Extract frame from sprite sheet
                frame.blit(sprite_sheet, (0, 0), (x, start_y, frame_width, frame_height))
                
                if colorkey:
                    frame.set_colorkey(colorkey)
                    
                # Cache the frame
                self.cache.add(frame_id, frame)
                
            # Apply transformations if needed
            if scale or flip:
                transform_key = f"s{scale}_f{flip}"
                transformed = self.cache.get_transformed(frame_id, transform_key)
                
                if not transformed:
                    transformed = frame.copy()
                    
                    if scale and (scale[0] != 1.0 or scale[1] != 1.0):
                        width = int(frame_width * scale[0])
                        height = int(frame_height * scale[1])
                        transformed = pygame.transform.scale(transformed, (width, height))
                        
                    if flip and (flip[0] or flip[1]):
                        transformed = pygame.transform.flip(transformed, flip[0], flip[1])
                        
                    self.cache.add_transformed(frame_id, transform_key, transformed)
                    
                frames.append(transformed)
            else:
                frames.append(frame)
                
        return frames
    
    def preload_resource(self, path: str, resource_id: str = None, resource_type: str = None) -> None:
        """
        Queue a resource for asynchronous loading.
        
        Args:
            path: Path to the resource
            resource_id: Optional ID for the resource (defaults to path)
            resource_type: Type of resource ('texture', 'sound', etc.)
        """
        resource_id = resource_id or path
        
        # Determine resource type from file extension if not specified
        if not resource_type:
            if path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                resource_type = 'texture'
            elif path.lower().endswith(('.wav', '.ogg', '.mp3')):
                resource_type = 'sound'
            else:
                print(f"Unknown resource type for {path}")
                return
                
        # Add to loading queue
        self.loading_queue.put((path, resource_id, resource_type))
        
        # Start loading thread if not already running
        if not self.loading_active:
            self._start_loading_thread()
    
    def preload_group(self, group_id: str, paths: List[Tuple[str, str, str]]) -> None:
        """
        Preload a group of resources.
        
        Args:
            group_id: ID for the group
            paths: List of (path, resource_id, resource_type) tuples
        """
        # Create a group if it doesn't exist
        if group_id not in self.preload_groups:
            self.preload_groups[group_id] = set()
            
        # Add resources to the group and queue them for loading
        for path, resource_id, resource_type in paths:
            resource_id = resource_id or path
            self.preload_groups[group_id].add(resource_id)
            self.preload_resource(path, resource_id, resource_type)
    
    def on_resource_loaded(self, resource_id: str, callback: Callable) -> None:
        """
        Register a callback to be called when a resource is loaded.
        
        Args:
            resource_id: ID of the resource
            callback: Function to call when the resource is loaded
        """
        if resource_id not in self.loading_callbacks:
            self.loading_callbacks[resource_id] = []
            
        self.loading_callbacks[resource_id].append(callback)
    
    def on_group_loaded(self, group_id: str, callback: Callable) -> None:
        """
        Register a callback to be called when all resources in a group are loaded.
        
        Args:
            group_id: ID of the group
            callback: Function to call when all resources in the group are loaded
        """
        # Create a special resource ID for the group
        group_resource_id = f"__group_{group_id}"
        
        if group_resource_id not in self.loading_callbacks:
            self.loading_callbacks[group_resource_id] = []
            
        self.loading_callbacks[group_resource_id].append(callback)
    
    def _start_loading_thread(self) -> None:
        """Start the background loading thread."""
        if self.loading_thread and self.loading_thread.is_alive():
            return
            
        self.loading_active = True
        self.loading_thread = threading.Thread(target=self._loading_worker)
        self.loading_thread.daemon = True
        self.loading_thread.start()
    
    def _loading_worker(self) -> None:
        """Background worker for loading resources."""
        loaded_resources = set()
        
        try:
            while self.loading_active:
                try:
                    # Get the next resource to load (with a timeout to allow checking if we should stop)
                    path, resource_id, resource_type = self.loading_queue.get(timeout=0.1)
                    
                    # Skip if already loaded
                    if self.cache.get(resource_id):
                        self.loading_queue.task_done()
                        continue
                        
                    # Load the resource
                    if resource_type == 'texture':
                        self.load_texture(path, resource_id)
                    elif resource_type == 'sound':
                        self.load_sound(path, resource_id)
                        
                    # Call callbacks for this resource
                    if resource_id in self.loading_callbacks:
                        for callback in self.loading_callbacks[resource_id]:
                            callback(resource_id)
                            
                    # Track loaded resources for group callbacks
                    loaded_resources.add(resource_id)
                    
                    # Check if any groups are complete
                    for group_id, resources in self.preload_groups.items():
                        if resources.issubset(loaded_resources):
                            # Call group callbacks
                            group_resource_id = f"__group_{group_id}"
                            if group_resource_id in self.loading_callbacks:
                                for callback in self.loading_callbacks[group_resource_id]:
                                    callback(group_id)
                                    
                    self.loading_queue.task_done()
                    
                except queue.Empty:
                    # No more resources to load
                    if self.loading_queue.empty():
                        self.loading_active = False
                        break
        except Exception as e:
            print(f"Error in loading thread: {e}")
            self.loading_active = False
    
    def clear_cache(self) -> None:
        """Clear all resources from the cache."""
        self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the resource manager."""
        return {
            'cache': self.cache.get_stats(),
            'loading_queue_size': self.loading_queue.qsize(),
            'loading_active': self.loading_active,
            'preload_groups': {
                group_id: len(resources)
                for group_id, resources in self.preload_groups.items()
            }
        }
