"""Search environment with grid-based coverage tracking."""

import numpy as np
from typing import Tuple, Set


class SearchEnvironment:
    """Environment for URC search with grid-based coverage tracking."""
    
    def __init__(self, radius: float, grid_size: float):
        """
        Initialize search environment.
        
        Args:
            radius: Search radius in meters (10m for URC)
            grid_size: Size of each grid cell in meters
        """
        self.radius = radius
        self.grid_size = grid_size
        self.diameter = radius * 2
        self.grid_cells = int(self.diameter / grid_size)
        
        # Coverage grid: True if cell has been seen, False otherwise
        self.coverage_grid = np.zeros((self.grid_cells, self.grid_cells), dtype=bool)
        
        # Center of the search area (in grid coordinates)
        self.center = self.grid_cells // 2
    
    def world_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        """
        Convert world coordinates to grid coordinates.
        World coordinates: center is (0, 0), range is [-radius, +radius]
        Grid coordinates: top-left is (0, 0), range is [0, grid_cells-1]
        """
        grid_x = int((x + self.radius) / self.grid_size)
        grid_y = int((y + self.radius) / self.grid_size)
        return grid_x, grid_y
    
    def grid_to_world(self, grid_x: int, grid_y: int) -> Tuple[float, float]:
        """Convert grid coordinates to world coordinates."""
        x = grid_x * self.grid_size - self.radius + self.grid_size / 2
        y = grid_y * self.grid_size - self.radius + self.grid_size / 2
        return x, y
    
    def is_within_bounds(self, grid_x: int, grid_y: int) -> bool:
        """Check if grid coordinates are within bounds."""
        return 0 <= grid_x < self.grid_cells and 0 <= grid_y < self.grid_cells
    
    def is_within_search_area(self, x: float, y: float) -> bool:
        """Check if world coordinates are within the circular search area."""
        distance = np.sqrt(x**2 + y**2)
        return distance <= self.radius
    
    def mark_cells_as_seen(self, cells: Set[Tuple[int, int]]):
        """Mark a set of grid cells as seen."""
        for grid_x, grid_y in cells:
            if self.is_within_bounds(grid_x, grid_y):
                self.coverage_grid[grid_y, grid_x] = True
    
    def get_coverage_percentage(self) -> float:
        """Calculate percentage of search area covered."""
        # Only count cells within the circular search radius
        total_cells = 0
        seen_cells = 0
        
        for i in range(self.grid_cells):
            for j in range(self.grid_cells):
                x, y = self.grid_to_world(j, i)
                if self.is_within_search_area(x, y):
                    total_cells += 1
                    if self.coverage_grid[i, j]:
                        seen_cells += 1
        
        return (seen_cells / total_cells * 100) if total_cells > 0 else 0.0
    
    def reset_coverage(self):
        """Reset all coverage data."""
        self.coverage_grid.fill(False)
