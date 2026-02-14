"""Visualization for URC robot search with 2D and 3D views."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, Rectangle
from mpl_toolkits.mplot3d import Axes3D
from typing import Optional

from environment import SearchEnvironment
from robot import SearchRobot
import config


class SearchVisualizer:
    """Dual-view visualizer for URC robot search."""
    
    def __init__(self, environment: SearchEnvironment, robot: SearchRobot):
        self.environment = environment
        self.robot = robot
        
        # Create figure with two subplots
        self.fig = plt.figure(figsize=(16, 7))
        self.ax_2d = self.fig.add_subplot(121)  # 2D top-down view
        self.ax_3d = self.fig.add_subplot(122, projection='3d')  # 3D view
        
        self._setup_2d_plot()
        self._setup_3d_plot()
        
        plt.tight_layout()
    
    def _setup_2d_plot(self):
        """Set up 2D top-down view."""
        self.ax_2d.set_xlim(-config.SEARCH_RADIUS, config.SEARCH_RADIUS)
        self.ax_2d.set_ylim(-config.SEARCH_RADIUS, config.SEARCH_RADIUS)
        self.ax_2d.set_xlabel('X (meters)', fontsize=10)
        self.ax_2d.set_ylabel('Y (meters)', fontsize=10)
        self.ax_2d.set_title('2D Top-Down View', fontsize=12, fontweight='bold')
        self.ax_2d.set_aspect('equal')
        self.ax_2d.grid(True, alpha=0.3)
        
        # Draw search boundary circle
        boundary = Circle((0, 0), config.SEARCH_RADIUS, 
                         fill=False, edgecolor='white', linewidth=2, linestyle='--')
        self.ax_2d.add_patch(boundary)
    
    def _setup_3d_plot(self):
        """Set up 3D view."""
        self.ax_3d.set_xlim(-config.SEARCH_RADIUS, config.SEARCH_RADIUS)
        self.ax_3d.set_ylim(-config.SEARCH_RADIUS, config.SEARCH_RADIUS)
        self.ax_3d.set_zlim(0, 2)
        self.ax_3d.set_xlabel('X (m)', fontsize=9)
        self.ax_3d.set_ylabel('Y (m)', fontsize=9)
        self.ax_3d.set_zlabel('Height (m)', fontsize=9)
        self.ax_3d.set_title('3D View', fontsize=12, fontweight='bold')
        
        # Set viewing angle
        self.ax_3d.view_init(elev=30, azim=45)
    
    def update(self, frame: int):
        """Update visualization."""
        self.ax_2d.clear()
        self.ax_3d.clear()
        self._setup_2d_plot()
        self._setup_3d_plot()
        
        # Update 2D view
        self._draw_2d_view()
        
        # Update 3D view
        self._draw_3d_view()
        
        return self.ax_2d, self.ax_3d
    
    def _draw_2d_view(self):
        """Draw 2D top-down view with grid coverage."""
        # Draw grid cells
        for i in range(self.environment.grid_cells):
            for j in range(self.environment.grid_cells):
                x, y = self.environment.grid_to_world(j, i)
                
                # Only draw cells within search radius
                if not self.environment.is_within_search_area(x, y):
                    continue
                
                # Determine color based on coverage
                if self.environment.coverage_grid[i, j]:
                    color = config.SEEN_COLOR
                    alpha = 0.6
                else:
                    color = config.UNSEEN_COLOR
                    alpha = 0.8
                
                # Draw grid cell
                rect = Rectangle((x - config.GRID_SIZE/2, y - config.GRID_SIZE/2),
                               config.GRID_SIZE, config.GRID_SIZE,
                               facecolor=color, edgecolor='gray', 
                               linewidth=0.1, alpha=alpha)
                self.ax_2d.add_patch(rect)
        
        # Draw robot path
        if config.SHOW_ROBOT_PATH and len(self.robot.path) > 1:
            path_array = np.array(self.robot.path)
            self.ax_2d.plot(path_array[:, 0], path_array[:, 1], 
                          'yellow', linewidth=2, alpha=0.7, label='Path')
        
        # Draw camera FOV cone
        if config.SHOW_FOV_CONE:
            self._draw_fov_cone_2d()
        
        # Draw robot
        robot_marker = Circle((self.robot.x, self.robot.y), 0.3,
                             facecolor=config.ROBOT_COLOR, edgecolor='white',
                             linewidth=2, zorder=10)
        self.ax_2d.add_patch(robot_marker)
        
        # Draw heading indicator
        heading_rad = np.radians(self.robot.heading)
        dx = 0.6 * np.sin(heading_rad)
        dy = 0.6 * np.cos(heading_rad)
        self.ax_2d.arrow(self.robot.x, self.robot.y, dx, dy,
                        head_width=0.3, head_length=0.2, 
                        fc='white', ec='white', linewidth=2, zorder=11)
        
        # Add info text
        coverage = self.environment.get_coverage_percentage()
        info_text = f'Coverage: {coverage:.1f}%\n'
        info_text += f'Position: ({self.robot.x:.1f}, {self.robot.y:.1f})m\n'
        info_text += f'Heading: {self.robot.heading:.0f}°'
        
        self.ax_2d.text(0.02, 0.98, info_text,
                       transform=self.ax_2d.transAxes,
                       fontsize=10, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # Re-add boundary
        boundary = Circle((0, 0), config.SEARCH_RADIUS,
                         fill=False, edgecolor='cyan', linewidth=2, linestyle='--')
        self.ax_2d.add_patch(boundary)
    
    def _draw_fov_cone_2d(self):
        """Draw camera field of view cone in 2D."""
        # Robot heading: 0° = North (+Y), 90° = East (+X)
        # Matplotlib Wedge: 0° = East (+X), angles go counter-clockwise
        # Conversion: matplotlib_angle = 90 - robot_heading
        
        fov_half = config.CAMERA_FOV_HORIZONTAL / 2
        center_angle_mpl = 90 - self.robot.heading
        
        start_angle = center_angle_mpl - fov_half
        end_angle = center_angle_mpl + fov_half
        
        # Draw FOV wedge
        wedge = Wedge((self.robot.x, self.robot.y), config.CAMERA_MAX_RANGE,
                     start_angle, end_angle,
                     facecolor='cyan', alpha=0.2, edgecolor='cyan', linewidth=1.5)
        self.ax_2d.add_patch(wedge)
    
    def _draw_3d_view(self):
        """Draw 3D view with coverage visualization."""
        # Draw base grid as bars
        for i in range(self.environment.grid_cells):
            for j in range(self.environment.grid_cells):
                x, y = self.environment.grid_to_world(j, i)
                
                if not self.environment.is_within_search_area(x, y):
                    continue
                
                # Determine height and color
                if self.environment.coverage_grid[i, j]:
                    height = 0.1
                    color = config.SEEN_COLOR
                    alpha = 0.7
                else:
                    height = 0.05
                    color = config.UNSEEN_COLOR
                    alpha = 0.8
                
                # Draw as 3D bar
                self._draw_3d_bar(x, y, 0, config.GRID_SIZE, config.GRID_SIZE, 
                                height, color, alpha)
        
        # Draw robot as cone/pyramid
        self._draw_robot_3d()
        
        # Draw search boundary cylinder
        theta = np.linspace(0, 2*np.pi, 50)
        x_circle = config.SEARCH_RADIUS * np.cos(theta)
        y_circle = config.SEARCH_RADIUS * np.sin(theta)
        z_bottom = np.zeros_like(theta)
        z_top = np.ones_like(theta) * 0.5
        
        # Draw vertical lines for cylinder
        for i in range(0, len(theta), 5):
            self.ax_3d.plot([x_circle[i], x_circle[i]], 
                           [y_circle[i], y_circle[i]],
                           [z_bottom[i], z_top[i]], 
                           'cyan', alpha=0.3, linewidth=0.5)
        
        # Draw top and bottom circles
        self.ax_3d.plot(x_circle, y_circle, z_bottom, 'cyan', alpha=0.5, linewidth=1.5)
        self.ax_3d.plot(x_circle, y_circle, z_top, 'cyan', alpha=0.5, linewidth=1.5)
        
        # Add coverage percentage text
        coverage = self.environment.get_coverage_percentage()
        self.ax_3d.text2D(0.05, 0.95, f'Coverage: {coverage:.1f}%',
                         transform=self.ax_3d.transAxes,
                         fontsize=11, fontweight='bold',
                         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    def _draw_3d_bar(self, x, y, z, dx, dy, dz, color, alpha):
        """Draw a 3D bar (rectangular prism)."""
        # Define vertices of a cube
        xx = [x - dx/2, x + dx/2]
        yy = [y - dy/2, y + dy/2]
        zz = [z, z + dz]
        
        # Draw bottom and top faces
        for z_val in zz:
            xs = [xx[0], xx[1], xx[1], xx[0], xx[0]]
            ys = [yy[0], yy[0], yy[1], yy[1], yy[0]]
            zs = [z_val] * 5
            self.ax_3d.plot(xs, ys, zs, color=color, alpha=alpha, linewidth=0.5)
    
    def _draw_robot_3d(self):
        """Draw robot as a 3D shape."""
        # Draw robot body as a cylinder/cone
        robot_height = 0.5
        robot_radius = 0.3
        
        # Create cone for robot body
        theta = np.linspace(0, 2*np.pi, 20)
        x_base = self.robot.x + robot_radius * np.cos(theta)
        y_base = self.robot.y + robot_radius * np.sin(theta)
        z_base = np.zeros_like(theta)
        
        # Draw base circle
        self.ax_3d.plot(x_base, y_base, z_base, config.ROBOT_COLOR, linewidth=2)
        
        # Draw lines to top point (heading direction)
        heading_rad = np.radians(self.robot.heading)
        top_x = self.robot.x + 0.2 * np.sin(heading_rad)
        top_y = self.robot.y + 0.2 * np.cos(heading_rad)
        top_z = robot_height
        
        for i in range(0, len(theta), 3):
            self.ax_3d.plot([x_base[i], top_x], [y_base[i], top_y], 
                           [z_base[i], top_z], config.ROBOT_COLOR, 
                           alpha=0.6, linewidth=1)
        
        # Draw heading arrow on top
        self.ax_3d.plot([self.robot.x, top_x], [self.robot.y, top_y], 
                       [top_z, top_z], 'white', linewidth=3, marker='o')

