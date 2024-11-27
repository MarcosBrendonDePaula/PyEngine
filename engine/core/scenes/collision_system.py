from typing import Set, Tuple, List
from ..components.collider import Collider
from ..components.physics import Physics
from ..entity import Entity

class CollisionSystem:
    def __init__(self):
        self._collision_pairs: Set[Tuple[int, int]] = set()

    def _resolve_collisions(self, entity1: Entity, entity2: Entity):
        """Resolve collisions between two entities"""
        collider1 = entity1.get_component(Collider)
        collider2 = entity2.get_component(Collider)
        physics1 = entity1.get_component(Physics)
        physics2 = entity2.get_component(Physics)

        if physics1 and not physics1.is_kinematic:
            physics1.resolve_collision(collider2)
        if physics2 and not physics2.is_kinematic:
            physics2.resolve_collision(collider1)

    def update(self, entities: List[Entity]):
        """Update collision detection and resolution"""
        # Clear previous collision pairs
        old_collision_pairs = self._collision_pairs.copy()
        self._collision_pairs.clear()

        # Get all entities with colliders
        entities_with_colliders = [
            entity for entity in entities
            if entity.get_component(Collider) is not None
        ]

        # Check each pair of entities
        for i in range(len(entities_with_colliders)):
            for j in range(i + 1, len(entities_with_colliders)):
                entity1 = entities_with_colliders[i]
                entity2 = entities_with_colliders[j]
                collider1 = entity1.get_component(Collider)
                collider2 = entity2.get_component(Collider)

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

        # Check for collision exits
        for pair in old_collision_pairs:
            if pair not in self._collision_pairs:
                # Find the entities
                entity1 = next((e for e in entities if e.id == pair[0]), None)
                entity2 = next((e for e in entities if e.id == pair[1]), None)
                if entity1 and entity2:
                    collider1 = entity1.get_component(Collider)
                    collider2 = entity2.get_component(Collider)
                    if collider1 and collider2:
                        collider1.on_collision_exit(entity2)
                        collider2.on_collision_exit(entity1)

    def get_colliding_pairs(self) -> Set[Tuple[int, int]]:
        """Get the current set of colliding entity pairs"""
        return self._collision_pairs.copy()

    def clear(self):
        """Clear all collision pairs"""
        self._collision_pairs.clear()
