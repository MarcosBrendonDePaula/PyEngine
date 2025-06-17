from typing import Set, Tuple, List, Dict, Optional
from ..components.collider import Collider
from ..components.physics import Physics
from ..entity import Entity

class SpatialGrid:
    """Grid espacial para otimizar detecção de colisões"""
    def __init__(self, cell_size: float = 100.0):
        self.cell_size = cell_size
        self.grid: Dict[Tuple[int, int], List[Entity]] = {}
    
    def clear(self):
        self.grid.clear()
    
    def _get_cell_coords(self, x: float, y: float) -> Tuple[int, int]:
        return (int(x // self.cell_size), int(y // self.cell_size))
    
    def insert(self, entity: Entity, collider: Collider):
        """Insere uma entidade na grid baseado na posição do collider"""
        # Assumindo que o collider tem posição x, y
        cell = self._get_cell_coords(collider.x, collider.y)
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(entity)
    
    def get_nearby_entities(self, entity: Entity, collider: Collider) -> List[Entity]:
        """Retorna entidades próximas (mesma célula e células adjacentes)"""
        nearby = []
        center_cell = self._get_cell_coords(collider.x, collider.y)
        
        # Verifica célula atual e adjacentes (3x3)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                cell = (center_cell[0] + dx, center_cell[1] + dy)
                if cell in self.grid:
                    for other_entity in self.grid[cell]:
                        if other_entity != entity:
                            nearby.append(other_entity)
        
        return nearby

class CollisionSystem:
    def __init__(self, use_spatial_partitioning: bool = True, grid_cell_size: float = 100.0):
        self._collision_pairs: Set[Tuple[int, int]] = set()
        self._entity_cache: Dict[int, Entity] = {}
        self._collider_cache: Dict[int, Collider] = {}
        self._physics_cache: Dict[int, Physics] = {}
        
        # Spatial partitioning
        self.use_spatial_partitioning = use_spatial_partitioning
        self.spatial_grid = SpatialGrid(grid_cell_size) if use_spatial_partitioning else None
        
        # Cache para UI entities
        self._ui_entity_ids: Set[int] = set()
        self._last_ui_check_frame = -1
        self._current_frame = 0
    
    def _update_caches(self, entities: List[Entity]):
        """Atualiza os caches de componentes para evitar lookups repetidos"""
        self._entity_cache.clear()
        self._collider_cache.clear()
        self._physics_cache.clear()
        
        for entity in entities:
            if hasattr(entity, 'get_component'):
                collider = entity.get_component(Collider)
                if collider is not None:
                    self._entity_cache[entity.id] = entity
                    self._collider_cache[entity.id] = collider
                    
                    physics = entity.get_component(Physics)
                    if physics:
                        self._physics_cache[entity.id] = physics
    
    def _update_ui_cache(self, entities: List[Entity]):
        """Atualiza cache de entidades UI (menos frequentemente)"""
        if self._current_frame - self._last_ui_check_frame > 60:  # A cada 60 frames
            self._ui_entity_ids.clear()
            for entity in entities:
                if hasattr(entity, 'scene') and entity.scene:
                    ui_entities = entity.scene.get_entities_by_group("ui")
                    if entity in ui_entities:
                        self._ui_entity_ids.add(entity.id)
            self._last_ui_check_frame = self._current_frame
    
    def _get_entities_with_colliders(self, entities: List[Entity]) -> List[Entity]:
        """Otimizado: retorna entidades com colliders, excluindo UI"""
        result = []
        
        for entity_id, entity in self._entity_cache.items():
            # Skip UI entities usando cache
            if entity_id in self._ui_entity_ids:
                continue
            result.append(entity)
        
        return result
    
    def _resolve_collisions(self, entity1: Entity, entity2: Entity):
        """Resolve collisions between two entities (otimizado com cache)"""
        # Usar cache para evitar lookups
        collider1 = self._collider_cache.get(entity1.id)
        collider2 = self._collider_cache.get(entity2.id)
        physics1 = self._physics_cache.get(entity1.id)
        physics2 = self._physics_cache.get(entity2.id)
        
        # Call on_collision handlers if they exist
        if hasattr(entity1, 'on_collision'):
            entity1.on_collision(entity2)
        if hasattr(entity2, 'on_collision'):
            entity2.on_collision(entity1)
        
        # Physics resolution
        if physics1 and not physics1.is_kinematic:
            physics1.resolve_collision(collider2)
        if physics2 and not physics2.is_kinematic:
            physics2.resolve_collision(collider1)
    
    def _broad_phase_collision_detection(self, entities_with_colliders: List[Entity]) -> List[Tuple[Entity, Entity]]:
        """Fase ampla de detecção usando spatial partitioning ou força bruta otimizada"""
        potential_pairs = []
        
        if self.use_spatial_partitioning and self.spatial_grid:
            # Usar spatial grid
            self.spatial_grid.clear()
            
            # Inserir todas as entidades na grid
            for entity in entities_with_colliders:
                collider = self._collider_cache[entity.id]
                self.spatial_grid.insert(entity, collider)
            
            # Verificar colisões apenas entre entidades próximas
            checked_pairs = set()
            for entity in entities_with_colliders:
                collider = self._collider_cache[entity.id]
                nearby_entities = self.spatial_grid.get_nearby_entities(entity, collider)
                
                for other_entity in nearby_entities:
                    # Evitar pares duplicados
                    pair_key = tuple(sorted([entity.id, other_entity.id]))
                    if pair_key not in checked_pairs:
                        potential_pairs.append((entity, other_entity))
                        checked_pairs.add(pair_key)
        else:
            # Força bruta otimizada (como antes, mas usando cache)
            for i in range(len(entities_with_colliders)):
                for j in range(i + 1, len(entities_with_colliders)):
                    potential_pairs.append((entities_with_colliders[i], entities_with_colliders[j]))
        
        return potential_pairs
    
    def update(self, entities: List[Entity]):
        """Update collision detection and resolution (versão otimizada)"""
        self._current_frame += 1
        
        # Atualizar caches
        self._update_caches(entities)
        self._update_ui_cache(entities)
        
        # Clear previous collision pairs
        old_collision_pairs = self._collision_pairs.copy()
        self._collision_pairs.clear()
        
        # Get entities with colliders (otimizado)
        entities_with_colliders = self._get_entities_with_colliders(entities)
        
        if len(entities_with_colliders) < 2:
            return  # Early return se não há pares suficientes
        
        # Broad phase: encontrar pares potenciais
        potential_pairs = self._broad_phase_collision_detection(entities_with_colliders)
        
        # Narrow phase: verificação precisa de colisão
        for entity1, entity2 in potential_pairs:
            collider1 = self._collider_cache[entity1.id]
            collider2 = self._collider_cache[entity2.id]
            
            if collider1.check_collision(collider2):
                # Add to current collision pairs
                collision_pair = tuple(sorted([entity1.id, entity2.id]))
                self._collision_pairs.add(collision_pair)
                
                # Resolve the collision
                self._resolve_collisions(entity1, entity2)
                
                # If this is a new collision, trigger collision enter
                if collision_pair not in old_collision_pairs:
                    collider1.on_collision_enter(entity2)
                    collider2.on_collision_enter(entity1)
        
        # Check for collision exits (otimizado)
        self._handle_collision_exits(old_collision_pairs)
    
    def _handle_collision_exits(self, old_collision_pairs: Set[Tuple[int, int]]):
        """Handle collision exits de forma otimizada"""
        for pair in old_collision_pairs:
            if pair not in self._collision_pairs:
                # Usar cache para encontrar entidades
                entity1 = self._entity_cache.get(pair[0])
                entity2 = self._entity_cache.get(pair[1])
                
                if entity1 and entity2:
                    collider1 = self._collider_cache.get(entity1.id)
                    collider2 = self._collider_cache.get(entity2.id)
                    
                    if collider1 and collider2:
                        collider1.on_collision_exit(entity2)
                        collider2.on_collision_exit(entity1)
    
    def get_colliding_pairs(self) -> Set[Tuple[int, int]]:
        """Get the current set of colliding entity pairs"""
        return self._collision_pairs.copy()
    
    def clear(self):
        """Clear all collision pairs and caches"""
        self._collision_pairs.clear()
        self._entity_cache.clear()
        self._collider_cache.clear()
        self._physics_cache.clear()
        self._ui_entity_ids.clear()
        if self.spatial_grid:
            self.spatial_grid.clear()
    
    def set_spatial_partitioning(self, enabled: bool, cell_size: float = 100.0):
        """Enable/disable spatial partitioning"""
        self.use_spatial_partitioning = enabled
        if enabled:
            self.spatial_grid = SpatialGrid(cell_size)
        else:
            self.spatial_grid = None