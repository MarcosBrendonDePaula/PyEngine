from typing import List, Tuple, Dict
import heapq

Grid = List[List[int]]  # 0 = walkable, 1 = obstacle


def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(start: Tuple[int, int], goal: Tuple[int, int], grid: Grid) -> List[Tuple[int, int]]:
    """Simple A* pathfinding on a grid."""
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
    g_score: Dict[Tuple[int, int], float] = {start: 0}
    f_score: Dict[Tuple[int, int], float] = {start: heuristic(start, goal)}

    neighbors = [(1,0),(-1,0),(0,1),(0,-1)]

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path
        for dx, dy in neighbors:
            nx, ny = current[0] + dx, current[1] + dy
            if ny < 0 or ny >= len(grid) or nx < 0 or nx >= len(grid[0]):
                continue
            if grid[ny][nx] == 1:
                continue
            tentative_g = g_score[current] + 1
            neighbor = (nx, ny)
            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return []
