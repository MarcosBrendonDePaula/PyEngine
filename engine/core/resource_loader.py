import pygame
import os

class ResourceLoader:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResourceLoader, cls).__new__(cls)
            cls._instance._resources = {}
            cls._instance._reference_count = {}
            print("ResourceLoader initialized")
        return cls._instance
    
    def load_resource(self, path: str, resource_id: str = None) -> any:
        """Load a resource and cache it. If resource_id is not provided, use path as id."""
        if resource_id is None:
            resource_id = path
            
        # If resource is already loaded, increment reference count and return it
        if resource_id in self._resources:
            self._reference_count[resource_id] += 1
            print(f"Resource {resource_id} retrieved from cache")
            return self._resources[resource_id]
            
        try:
            if os.path.exists(path):
                print(f"Loading resource: {path}")
                if path.endswith('.png'):
                    resource = pygame.image.load(path).convert_alpha()
                elif path.endswith(('.jpg', '.jpeg')):
                    resource = pygame.image.load(path).convert()
                elif path.endswith('.wav'):
                    resource = pygame.mixer.Sound(path)
                elif path.endswith('.ogg') or path.endswith('.mp3'):
                    resource = pygame.mixer.Sound(path)
                else:
                    print(f"Unknown resource type for {path}")
                    return None
                    
                self._resources[resource_id] = resource
                self._reference_count[resource_id] = 1
                print(f"Successfully loaded: {path}")
                return resource
            else:
                print(f"Resource not found: {path}")
                return None
        except Exception as e:
            print(f"Failed to load resource {path}: {e}")
            return None
            
    def get_resource(self, resource_id: str) -> any:
        """Get a cached resource by its ID"""
        return self._resources.get(resource_id)
        
    def unload_resource(self, resource_id: str) -> None:
        """Decrement reference count and unload resource if no longer needed"""
        if resource_id in self._reference_count:
            self._reference_count[resource_id] -= 1
            if self._reference_count[resource_id] <= 0:
                if resource_id in self._resources:
                    resource = self._resources[resource_id]
                    # Properly clean up pygame resources
                    if isinstance(resource, pygame.Surface):
                        del resource
                    elif isinstance(resource, pygame.mixer.Sound):
                        resource.stop()
                    del self._resources[resource_id]
                    del self._reference_count[resource_id]
                    print(f"Resource {resource_id} unloaded")
                    
    def clear_unused_resources(self) -> None:
        """Clear all resources with reference count of 0"""
        for resource_id in list(self._reference_count.keys()):
            if self._reference_count[resource_id] <= 0:
                self.unload_resource(resource_id)
                
    def clear_all_resources(self) -> None:
        """Clear all resources regardless of reference count"""
        for resource_id in list(self._resources.keys()):
            self.unload_resource(resource_id)
            
    def get_resource_info(self) -> dict:
        """Get information about loaded resources"""
        return {
            'total_resources': len(self._resources),
            'resources': {
                rid: {
                    'type': type(res).__name__,
                    'ref_count': self._reference_count[rid]
                }
                for rid, res in self._resources.items()
            }
        }
