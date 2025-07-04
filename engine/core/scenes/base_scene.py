import pygame
from typing import List, Dict, Optional, Any, NamedTuple
from ..camera import Camera
from ..resource_loader import ResourceLoader
from .collision_system import CollisionSystem
from ..components.collider import Collider
from ..thread_pool import ThreadPool, get_global_thread_pool

class CollisionConfig(NamedTuple):
    """Configuração do sistema de colisão"""
    enabled: bool = True
    use_spatial_partitioning: bool = True
    grid_cell_size: float = 100.0
    max_entities_for_bruteforce: int = 50  # Usa força bruta se tiver menos entidades
    update_frequency: int = 1  # A cada quantos frames atualizar (1 = todo frame)
    ui_cache_update_interval: int = 60  # Frames entre atualizações do cache UI

class ThreadConfig(NamedTuple):
    """Configuração do sistema de threads"""
    enabled: bool = True
    max_workers: Optional[int] = None  # None = auto-detect CPU count
    min_entities_for_threading: int = 20  # Minimum entities to justify threading overhead
    batch_size_multiplier: float = 1.5  # Multiplier for optimal batch size calculation
    use_global_pool: bool = True  # Use shared thread pool or create scene-specific one

class BaseScene:
    def __init__(self, num_threads: int = None, collision_config: CollisionConfig = None, 
                 thread_config: ThreadConfig = None):
        self.entities = []
        self.entity_groups: Dict[str, List] = {}
        self.interface = None
        self._resources = {}  # For storing resource IDs
        self._is_initialized = False
        self._is_loaded = False
        self._loading_progress = 0
        self.camera = None  # Will be initialized when interface is set
        self.resource_loader = ResourceLoader()  # Get the singleton instance
        self.delta_time: float = 0.0  # Initialize delta_time
        
        # Thread configuration
        self._thread_config = thread_config or ThreadConfig()
        self._thread_pool = None
        self._init_thread_pool(num_threads)
        
        # Configuração do sistema de colisão
        self._collision_config = collision_config or CollisionConfig()
        self._collision_frame_counter = 0
        
        # Inicializar sistema de colisão com configurações
        if self._collision_config.enabled:
            self.collision_system = CollisionSystem(
                use_spatial_partitioning=self._collision_config.use_spatial_partitioning,
                grid_cell_size=self._collision_config.grid_cell_size
            )
            # Configurar intervalo de atualização do cache UI
            if hasattr(self.collision_system, '_ui_cache_update_interval'):
                self.collision_system._ui_cache_update_interval = self._collision_config.ui_cache_update_interval
        else:
            self.collision_system = None
            
    def _init_thread_pool(self, num_threads: Optional[int] = None):
        """Initialize thread pool for parallel entity updates."""
        if not self._thread_config.enabled:
            self._thread_pool = None
            return
            
        if self._thread_config.use_global_pool:
            self._thread_pool = get_global_thread_pool()
        else:
            # Create scene-specific thread pool
            max_workers = num_threads or self._thread_config.max_workers
            self._thread_pool = ThreadPool(max_workers=max_workers)
            
    def configure_threading(self, config: ThreadConfig):
        """Reconfigure threading system at runtime."""
        old_config = self._thread_config
        self._thread_config = config
        
        # Shutdown old thread pool if it was scene-specific
        if not old_config.use_global_pool and self._thread_pool:
            self._thread_pool.shutdown()
            
        # Initialize new thread pool
        self._init_thread_pool()
        
    def get_thread_config(self) -> ThreadConfig:
        """Get current thread configuration."""
        return self._thread_config
        
    def set_thread_count(self, num_threads: int):
        """Set number of threads for entity updates."""
        config = self._thread_config._replace(max_workers=num_threads, use_global_pool=False)
        self.configure_threading(config)
        
    def enable_threading(self, enabled: bool = True):
        """Enable or disable threaded entity updates."""
        config = self._thread_config._replace(enabled=enabled)
        self.configure_threading(config)
        
    def disable_threading(self):
        """Disable threaded entity updates."""
        self.enable_threading(False)
        
    def configure_collision_system(self, config: CollisionConfig):
        """Reconfigura o sistema de colisão em tempo de execução"""
        old_config = self._collision_config
        self._collision_config = config
        
        if not config.enabled:
            # Desabilitar sistema de colisão
            if self.collision_system:
                self.collision_system.clear()
                self.collision_system = None
        elif not old_config.enabled and config.enabled:
            # Reabilitar sistema de colisão
            self.collision_system = CollisionSystem(
                use_spatial_partitioning=config.use_spatial_partitioning,
                grid_cell_size=config.grid_cell_size
            )
        elif self.collision_system:
            # Atualizar configurações existentes
            self.collision_system.set_spatial_partitioning(
                config.use_spatial_partitioning, 
                config.grid_cell_size
            )
    
    def get_collision_config(self) -> CollisionConfig:
        """Retorna a configuração atual do sistema de colisão"""
        return self._collision_config
    
    def set_collision_spatial_partitioning(self, enabled: bool, cell_size: float = None):
        """Atalho para configurar spatial partitioning"""
        if self.collision_system:
            cell_size = cell_size or self._collision_config.grid_cell_size
            self.collision_system.set_spatial_partitioning(enabled, cell_size)
            # Atualizar configuração
            self._collision_config = self._collision_config._replace(
                use_spatial_partitioning=enabled,
                grid_cell_size=cell_size
            )
    
    def disable_collision_system(self):
        """Desabilita completamente o sistema de colisão"""
        self.configure_collision_system(
            self._collision_config._replace(enabled=False)
        )
    
    def enable_collision_system(self):
        """Reabilita o sistema de colisão"""
        self.configure_collision_system(
            self._collision_config._replace(enabled=True)
        )

    def initialize(self):
        """Initialize scene resources. Called once when scene is added to manager."""
        if not self._is_initialized:
            self._is_initialized = True
            self.on_initialize()

    def on_initialize(self):
        """Override this method to perform one-time initialization"""
        pass

    def on_enter(self, previous_scene):
        """Called when scene becomes active"""
        pass

    def on_exit(self):
        """Called when switching to another scene"""
        pass

    def on_pause(self):
        """Called when another scene is pushed on top"""
        pass

    def on_resume(self):
        """Called when scene is resumed (top scene was popped)"""
        pass

    def set_interface(self, interface):
        """Set the interface reference and initialize camera"""
        self.interface = interface
        if interface:
            self.camera = Camera(interface.size[0], interface.size[1])

    def add_entity(self, entity, group: str = "default"):
        """Add an entity to the scene and group"""
        if entity not in self.entities:  # Prevent duplicate entities
            self.entities.append(entity)
            if group not in self.entity_groups:
                self.entity_groups[group] = []
            if entity not in self.entity_groups[group]:
                self.entity_groups[group].append(entity)
            # Set scene reference in entity
            entity.scene = self

    def remove_entity(self, entity, group: str = "default"):
        """Remove an entity from the scene and group"""
        if entity in self.entities:
            self.entities.remove(entity)
        if group in self.entity_groups and entity in self.entity_groups[group]:
            self.entity_groups[group].remove(entity)
        # Remove scene reference
        entity.scene = None

    def get_entities_by_group(self, group: str) -> List:
        """Get all entities in a specific group"""
        return self.entity_groups.get(group, [])

    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events"""
        if not self._is_loaded:
            return
            
        for entity in self.entities:
            if entity.active:
                entity.handle_event(event)

    def update(self, delta_time: float):
        """Update all entities in the scene"""
        if not self._is_loaded:
            # If resources aren't loaded, update loading progress
            if not self._resources:
                self.load_resources()
            return

        self.delta_time = delta_time
        # Update camera first
        if self.camera:
            self.camera.update()

        # Update all active entities (with optional parallel processing)
        active_entities = [entity for entity in self.entities if entity.active]
        
        if (self._thread_config.enabled and self._thread_pool and 
            len(active_entities) >= self._thread_config.min_entities_for_threading):
            # Use parallel processing for large entity counts
            self._update_entities_parallel(active_entities, delta_time)
        else:
            # Use sequential processing for small entity counts or when threading is disabled
            self._update_entities_sequential(active_entities, delta_time)
            
    def _update_entities_parallel(self, entities: List, delta_time: float):
        """Update entities using parallel processing."""
        try:
            min_batch_size = max(5, int(self._thread_config.min_entities_for_threading * 0.5))
            self._thread_pool.update_entities_parallel(entities, delta_time, min_batch_size)
        except Exception as e:
            print(f"Error in parallel entity update, falling back to sequential: {e}")
            self._update_entities_sequential(entities, delta_time)
            
    def _update_entities_sequential(self, entities: List, delta_time: float):
        """Update entities sequentially (fallback method)."""
        for entity in entities:
            try:
                entity.delta_time = delta_time
                entity.update()
            except Exception as e:
                print(f"Error updating entity {entity.id}: {e}")

        # Update collision system com configurações
        if self.collision_system and self._collision_config.enabled:
            self._collision_frame_counter += 1
            
            # Verificar se deve atualizar colisões neste frame
            if self._collision_frame_counter >= self._collision_config.update_frequency:
                self._collision_frame_counter = 0
                
                # Escolher algoritmo baseado no número de entidades
                entities_with_colliders = [
                    e for e in self.entities 
                    if hasattr(e, 'get_component') and e.get_component(Collider) is not None
                ]
                
                # Auto-otimização: usar força bruta para poucas entidades
                if (len(entities_with_colliders) <= self._collision_config.max_entities_for_bruteforce and 
                    self._collision_config.use_spatial_partitioning):
                    self.collision_system.set_spatial_partitioning(False)
                    self.collision_system.update(self.entities)
                    self.collision_system.set_spatial_partitioning(True, self._collision_config.grid_cell_size)
                else:
                    self.collision_system.update(self.entities)

    def render(self, screen: pygame.Surface):
        """Render the scene"""
        if not self._is_loaded:
            self._render_loading_screen(screen)
            return

        # Fill background with black
        screen.fill((20, 20, 20))

        # Get camera offset
        camera_offset = (0, 0)
        if self.camera:
            camera_offset = (-self.camera.position.x, -self.camera.position.y)

        # First render non-UI entities with camera offset
        for entity in self.entities:
            if entity.visible and entity not in self.get_entities_by_group("ui"):
                entity.render(screen, camera_offset)

        # Then render UI entities without camera offset (in screen space)
        for entity in self.get_entities_by_group("ui"):
            if entity.visible:
                entity.render(screen, (0, 0))

    def _render_loading_screen(self, screen: pygame.Surface):
        """Render a simple loading screen"""
        screen.fill((20, 20, 20))
        if pygame.font.get_init():
            font = pygame.font.Font(None, 36)
            text = font.render(f"Loading... {self._loading_progress}%", True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(text, text_rect)

    def load_resources(self):
        """Override this to load scene-specific resources"""
        self._is_loaded = True
        self._loading_progress = 100

    def get_resource(self, name: str) -> Any:
        """Get a loaded resource by name"""
        if name in self._resources:
            return self.resource_loader.get_resource(self._resources[name])
        return None

    def add_resource(self, name: str, path: str) -> None:
        """Add a resource to the scene using the resource loader"""
        resource = self.resource_loader.load_resource(path, name)
        if resource:
            self._resources[name] = name

    def remove_resource(self, name: str) -> None:
        """Remove a resource from the scene"""
        if name in self._resources:
            self.resource_loader.unload_resource(self._resources[name])
            del self._resources[name]

    def cleanup(self):
        """Clean up scene resources"""
        # Clear entities
        for entity in self.entities[:]:  # Create a copy of the list to avoid modification during iteration
            self.remove_entity(entity)
        self.entity_groups.clear()
        
        # Clear resources
        for name in list(self._resources.keys()):
            self.remove_resource(name)
        self._resources.clear()
        self._is_loaded = False
        self._loading_progress = 0
        
        # Clear collision system
        if self.collision_system:
            self.collision_system.clear()
            
        # Shutdown scene-specific thread pool
        if not self._thread_config.use_global_pool and self._thread_pool:
            self._thread_pool.shutdown()

    # Métodos de conveniência para debugging e profiling
    def get_collision_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema de colisão"""
        if not self.collision_system:
            return {"enabled": False}
        
        entities_with_colliders = [
            e for e in self.entities 
            if hasattr(e, 'get_component') and e.get_component(Collider) is not None
        ]
        
        return {
            "enabled": self._collision_config.enabled,
            "spatial_partitioning": self._collision_config.use_spatial_partitioning,
            "grid_cell_size": self._collision_config.grid_cell_size,
            "entities_with_colliders": len(entities_with_colliders),
            "total_entities": len(self.entities),
            "current_collision_pairs": len(self.collision_system.get_colliding_pairs()),
            "update_frequency": self._collision_config.update_frequency
        }