import pygame
from typing import Tuple, List, Optional, Set, Callable
from ..component import Component
import math

def point_in_polygon(point: Tuple[float, float], vertices: List[Tuple[float, float]]) -> bool:
    """Check if a point is inside a polygon using ray casting algorithm"""
    x, y = point
    inside = False
    j = len(vertices) - 1
    
    for i in range(len(vertices)):
        if ((vertices[i][1] > y) != (vertices[j][1] > y) and
            x < (vertices[j][0] - vertices[i][0]) * (y - vertices[i][1]) /
                (vertices[j][1] - vertices[i][1]) + vertices[i][0]):
            inside = not inside
        j = i
    
    return inside

def get_line_segment_distance(point: Tuple[float, float], line_start: Tuple[float, float], line_end: Tuple[float, float]) -> float:
    """Get the distance from a point to a line segment"""
    line_vec = pygame.math.Vector2(line_end[0] - line_start[0], line_end[1] - line_start[1])
    point_vec = pygame.math.Vector2(point[0] - line_start[0], point[1] - line_start[1])
    line_len = line_vec.length()
    
    if line_len == 0:
        return point_vec.length()
        
    t = max(0, min(1, point_vec.dot(line_vec) / (line_len * line_len)))
    projection = pygame.math.Vector2(
        line_start[0] + t * line_vec.x,
        line_start[1] + t * line_vec.y
    )
    
    return pygame.math.Vector2(point[0] - projection.x, point[1] - projection.y).length()

def line_segments_intersect(p1: Tuple[float, float], p2: Tuple[float, float], 
                          p3: Tuple[float, float], p4: Tuple[float, float]) -> bool:
    """Check if two line segments intersect"""
    def ccw(A: Tuple[float, float], B: Tuple[float, float], C: Tuple[float, float]) -> bool:
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
    
    return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)

def polygons_intersect(poly1: List[Tuple[float, float]], poly2: List[Tuple[float, float]]) -> bool:
    """Check if two polygons intersect using edge intersection and point containment"""
    # Check if any point from one polygon is inside the other
    for point in poly1:
        if point_in_polygon(point, poly2):
            return True
    for point in poly2:
        if point_in_polygon(point, poly1):
            return True
    
    # Check if any edges intersect
    for i in range(len(poly1)):
        for j in range(len(poly2)):
            p1 = poly1[i]
            p2 = poly1[(i + 1) % len(poly1)]
            p3 = poly2[j]
            p4 = poly2[(j + 1) % len(poly2)]
            if line_segments_intersect(p1, p2, p3, p4):
                return True
    
    return False

class Collider(Component):
    def __init__(self, width: float, height: float, is_trigger: bool = False):
        super().__init__()
        self.width = width
        self.height = height
        self.is_trigger = is_trigger
        self.offset = pygame.math.Vector2(0, 0)
        self.colliding_entities: Set[int] = set()  # Set of colliding entity IDs
        self.collision_layer = 0
        self.collision_mask = 1 << 0  # By default, collide with layer 0
        self.debug_color = (255, 255, 0) if is_trigger else (255, 0, 0)
        self.show_debug = True  # Enable debug visualization by default
        self.line_thickness = 2  # Thicker lines for better visibility

    def get_rect(self) -> pygame.Rect:
        """Get the collision rectangle in world space"""
        if not self.entity:
            return pygame.Rect(0, 0, self.width, self.height)
        
        return pygame.Rect(
            self.entity.position.x + self.offset.x - self.width/2,
            self.entity.position.y + self.offset.y - self.height/2,
            self.width,
            self.height
        )

    def get_rect_points(self) -> List[Tuple[float, float]]:
        """Get rectangle corners as points for polygon collision"""
        rect = self.get_rect()
        return [
            (rect.left, rect.top),
            (rect.right, rect.top),
            (rect.right, rect.bottom),
            (rect.left, rect.bottom)
        ]

    def check_collision(self, other: 'Collider') -> bool:
        """Check if this collider intersects with another"""
        # Check collision layers
        if not (self.collision_mask & (1 << other.collision_layer)):
            return False

        # Check if other collider can collide with this layer
        if not (other.collision_mask & (1 << self.collision_layer)):
            return False

        if not self.entity or not other.entity:
            return False

        if isinstance(other, PolygonCollider):
            # Rectangle vs Polygon collision
            return polygons_intersect(self.get_rect_points(), other.get_world_points())
        elif isinstance(other, CircleCollider):
            # Rectangle vs Circle collision
            rect_points = self.get_rect_points()
            center = (
                other.entity.position.x + other.offset.x,
                other.entity.position.y + other.offset.y
            )
            
            # Check if circle center is inside rectangle
            if point_in_polygon(center, rect_points):
                return True
                
            # Check if any rectangle edge is closer to circle center than radius
            for i in range(len(rect_points)):
                p1 = rect_points[i]
                p2 = rect_points[(i + 1) % len(rect_points)]
                dist = get_line_segment_distance(center, p1, p2)
                if dist <= other.radius:
                    return True
            return False
        else:
            # Rectangle vs Rectangle collision
            return polygons_intersect(self.get_rect_points(), other.get_rect_points())

    def on_collision_enter(self, other_entity: 'Entity'):
        """Called when collision starts"""
        self.colliding_entities.add(other_entity.id)

    def on_collision_exit(self, other_entity: 'Entity'):
        """Called when collision ends"""
        self.colliding_entities.discard(other_entity.id)

    def set_collision_layer(self, layer: int):
        """Set the collision layer (0-31)"""
        self.collision_layer = min(max(layer, 0), 31)

    def set_collision_mask(self, mask: int):
        """Set the collision mask (which layers to collide with)"""
        self.collision_mask = mask

    def add_to_collision_mask(self, layer: int):
        """Add a layer to the collision mask"""
        self.collision_mask |= (1 << layer)

    def remove_from_collision_mask(self, layer: int):
        """Remove a layer from the collision mask"""
        self.collision_mask &= ~(1 << layer)

    def set_size(self, width: float, height: float):
        """Set the collider size"""
        self.width = width
        self.height = height

    def set_offset(self, x: float, y: float):
        """Set the collider offset from entity position"""
        self.offset.x = x
        self.offset.y = y

    def is_colliding_with(self, entity_id: int) -> bool:
        """Check if currently colliding with a specific entity"""
        return entity_id in self.colliding_entities

    def set_debug_color(self, color: Tuple[int, int, int]):
        """Set the debug visualization color"""
        self.debug_color = color

    def toggle_debug_visualization(self, show: bool):
        """Enable or disable debug visualization"""
        self.show_debug = show

    def render_debug(self, screen: pygame.Surface, camera_offset=(0, 0)):
        """Render collision bounds for debugging"""
        if not self.show_debug:
            return
            
        rect = self.get_rect()
        rect.x -= camera_offset[0]
        rect.y -= camera_offset[1]
        
        # Draw filled rectangle with alpha for better visibility
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (*self.debug_color, 50), s.get_rect())  # Semi-transparent fill
        screen.blit(s, rect)
        
        # Draw outline with specified thickness
        pygame.draw.rect(screen, self.debug_color, rect, self.line_thickness)
        
        # Draw vertices
        points = [(p[0] - camera_offset[0], p[1] - camera_offset[1]) for p in self.get_rect_points()]
        for point in points:
            pygame.draw.circle(screen, self.debug_color, point, 2)


class RectCollider(Collider):
    """Rectangular collider - same as base Collider for backwards compatibility"""
    pass


class CircleCollider(Collider):
    def __init__(self, radius: float, is_trigger: bool = False):
        super().__init__(radius * 2, radius * 2, is_trigger)
        self.radius = radius

    def check_collision(self, other: 'Collider') -> bool:
        # Check collision layers first
        if not (self.collision_mask & (1 << other.collision_layer)):
            return False

        # Check if other collider can collide with this layer
        if not (other.collision_mask & (1 << self.collision_layer)):
            return False

        if not self.entity or not other.entity:
            return False

        center = (
            self.entity.position.x + self.offset.x,
            self.entity.position.y + self.offset.y
        )

        if isinstance(other, CircleCollider):
            # Circle vs Circle collision
            other_center = (
                other.entity.position.x + other.offset.x,
                other.entity.position.y + other.offset.y
            )
            
            distance = math.sqrt(
                (center[0] - other_center[0])**2 + 
                (center[1] - other_center[1])**2
            )
            return distance < (self.radius + other.radius)
            
        elif isinstance(other, PolygonCollider):
            # Circle vs Polygon collision
            # Check if circle center is inside polygon
            if point_in_polygon(center, other.get_world_points()):
                return True
                
            # Check if any polygon edge is closer to circle center than radius
            points = other.get_world_points()
            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]
                dist = get_line_segment_distance(center, p1, p2)
                if dist <= self.radius:
                    return True
                    
            return False
            
        else:
            # Circle vs Rectangle collision
            return other.check_collision(self)

    def render_debug(self, screen: pygame.Surface, camera_offset=(0, 0)):
        if not self.show_debug or not self.entity:
            return

        center = (
            self.entity.position.x + self.offset.x - camera_offset[0],
            self.entity.position.y + self.offset.y - camera_offset[1]
        )
        
        # Draw filled circle with alpha
        s = pygame.Surface((self.radius * 2 + 2, self.radius * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.debug_color, 50), (self.radius + 1, self.radius + 1), self.radius)  # Semi-transparent fill
        screen.blit(s, (center[0] - self.radius - 1, center[1] - self.radius - 1))
        
        # Draw outline with specified thickness
        pygame.draw.circle(screen, self.debug_color, center, self.radius, self.line_thickness)
        # Draw center point
        pygame.draw.circle(screen, self.debug_color, center, 2)


class PolygonCollider(Collider):
    def __init__(self, points: List[Tuple[float, float]], is_trigger: bool = False):
        # Calculate bounding box for the polygon
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)
        width = max_x - min_x
        height = max_y - min_y
        
        super().__init__(width, height, is_trigger)
        self.points = points
        self.original_points = points.copy()  # Store original points for rotation
        self.rotation = 0  # Current rotation in degrees

    def get_world_points(self) -> List[Tuple[float, float]]:
        """Get polygon points in world space"""
        if not self.entity:
            return self.points

        world_points = []
        for x, y in self.points:
            world_x = self.entity.position.x + self.offset.x + x
            world_y = self.entity.position.y + self.offset.y + y
            world_points.append((world_x, world_y))
        return world_points

    def check_collision(self, other: 'Collider') -> bool:
        # Check collision layers first
        if not (self.collision_mask & (1 << other.collision_layer)):
            return False

        # Check if other collider can collide with this layer
        if not (other.collision_mask & (1 << self.collision_layer)):
            return False

        if not self.entity or not other.entity:
            return False

        if isinstance(other, PolygonCollider):
            # Polygon vs Polygon collision
            return polygons_intersect(self.get_world_points(), other.get_world_points())
            
        elif isinstance(other, CircleCollider):
            # Polygon vs Circle collision
            return other.check_collision(self)
            
        else:
            # Polygon vs Rectangle collision
            return polygons_intersect(self.get_world_points(), other.get_rect_points())

    def rotate(self, angle: float):
        """Rotate the polygon by given angle in degrees"""
        self.rotation = angle
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        self.points = []
        for x, y in self.original_points:
            new_x = x * cos_a - y * sin_a
            new_y = x * sin_a + y * cos_a
            self.points.append((new_x, new_y))

    def render_debug(self, screen: pygame.Surface, camera_offset=(0, 0)):
        if not self.show_debug:
            return
            
        world_points = self.get_world_points()
        # Adjust for camera offset
        points = [(x - camera_offset[0], y - camera_offset[1]) for x, y in world_points]
        
        if len(points) > 2:
            # Draw filled polygon with alpha
            s = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            pygame.draw.polygon(s, (*self.debug_color, 50), points)  # Semi-transparent fill
            screen.blit(s, (0, 0))
            
            # Draw outline with specified thickness
            pygame.draw.polygon(screen, self.debug_color, points, self.line_thickness)
            # Draw vertices
            for point in points:
                pygame.draw.circle(screen, self.debug_color, point, 2)
            # Draw center point
            if self.entity:
                center = (
                    self.entity.position.x + self.offset.x - camera_offset[0],
                    self.entity.position.y + self.offset.y - camera_offset[1]
                )
                pygame.draw.circle(screen, self.debug_color, center, 2)
