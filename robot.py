"""Robot class for URC search with camera field of view."""

import numpy as np
from typing import List, Tuple, Set, Callable, Optional


class SearchRobot:
    """Robot with Intel RealSense D435 camera for URC search."""
    
    def __init__(self, start_x: float, start_y: float, speed: float,
                 fov_h: float, fov_v: float, camera_range: float):
        """
        Initialize search robot.
        
        Args:
            start_x, start_y: Starting position in world coordinates
            speed: Robot speed in m/s
            fov_h: Horizontal field of view in degrees
            fov_v: Vertical field of view in degrees
            camera_range: Maximum camera range in meters
        """
        self.x = start_x
        self.y = start_y
        self.heading = 0.0  # Heading in degrees (0 = North/+Y, 90 = East/+X)
        self.speed = speed
        
        # Camera parameters
        self.fov_horizontal = fov_h
        self.fov_vertical = fov_v
        self.camera_range = camera_range
        
        # Path history
        self.path: List[Tuple[float, float]] = [(self.x, self.y)]
        
        # Search algorithm function
        self.search_function: Optional[Callable] = None
    
    def set_search_algorithm(self, func: Callable):
        """
        Set the search algorithm function.
        
        The function should take (robot, time_step) as parameters and
        update the robot's position and heading.
        """
        self.search_function = func
    
    def move(self, dx: float, dy: float):
        """Move robot by relative distance."""
        self.x += dx
        self.y += dy
        self.path.append((self.x, self.y))
    
    def move_forward(self, distance: float):
        """Move robot forward in current heading direction."""
        heading_rad = np.radians(self.heading)
        dx = distance * np.sin(heading_rad)
        dy = distance * np.cos(heading_rad)
        self.move(dx, dy)
    
    def turn(self, angle_degrees: float):
        """Turn robot by angle in degrees (positive = clockwise)."""
        self.heading = (self.heading + angle_degrees) % 360
    
    def set_heading(self, angle_degrees: float):
        """Set absolute heading in degrees."""
        self.heading = angle_degrees % 360
    
    def get_visible_cells(self, grid_size: float) -> Set[Tuple[int, int]]:
        """
        Calculate which grid cells are visible to the camera.
        Returns set of (grid_x, grid_y) tuples.
        """
        visible_cells = set()
        
        # Convert heading to radians
        heading_rad = np.radians(self.heading)
        
        # Calculate FOV cone boundaries (using horizontal FOV for 2D)
        fov_rad = np.radians(self.fov_horizontal)
        half_fov = fov_rad / 2
        
        # Sample points within the FOV cone
        num_angle_samples = 20
        num_distance_samples = int(self.camera_range / grid_size) + 1
        
        for angle_offset in np.linspace(-half_fov, half_fov, num_angle_samples):
            direction_angle = heading_rad + angle_offset
            
            for distance in np.linspace(0, self.camera_range, num_distance_samples):
                # Calculate point in world coordinates
                px = self.x + distance * np.sin(direction_angle)
                py = self.y + distance * np.cos(direction_angle)
                
                # Convert to grid coordinates (need to import from environment)
                # We'll do this conversion in the step function
                visible_cells.add((px, py))
        
        return visible_cells
    
    def step(self, time_step: float):
        """Execute one time step of the search algorithm."""
        if self.search_function:
            self.search_function(self, time_step)
    
    def get_position(self) -> Tuple[float, float]:
        """Get current position."""
        return (self.x, self.y)
    
    def get_heading(self) -> float:
        """Get current heading in degrees."""
        return self.heading
