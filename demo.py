#!/usr/bin/env python3
"""
Quick demo showing how to run the visualization with a custom algorithm.
Run this file directly instead of main.py if you want to test a single algorithm.
"""

import numpy as np
from environment import SearchEnvironment
from robot import SearchRobot
from visualizer import SearchVisualizer
import config
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider


def my_custom_algorithm(robot: SearchRobot, time_step: float):
    """
    Archimedean spiral path based on ROS2 SpiralPathGenerator.
    
    Matches the C++ implementation which builds a spiral path where:
    - radius_step: How much radius increases per full rotation (360 degrees)
    - angle_step_deg: Angular resolution between path points
    - max_radius: Maximum spiral radius before stopping
    
    C++ generates the full path first, we follow it incrementally.
    """
    if not hasattr(robot, '_spiral_state'):
        # Configuration parameters (matching C++ node parameters)
        robot._spiral_state = {
            'start_x': 0.0,
            'start_y': 0.0,
            'radius_step': 5.0,  # radius increases by this amount per 360° rotation
            'angle_step_deg': 5.0,  # degrees between waypoints (5° matches C++)
            'max_radius': 10.0,  # maximum radius of spiral
            
            # Path following state
            'current_angle_deg': 0.0,
            'complete': False,
        }
        
        state = robot._spiral_state
        print(f"Spiral parameters: radius_step={state['radius_step']}m, "
              f"angle_step={state['angle_step_deg']}°, max_radius={state['max_radius']}m")
    
    state = robot._spiral_state
    
    # Check if spiral is complete
    if state['complete']:
        return
    
    # Calculate current radius based on angle
    current_radius = (state['current_angle_deg'] / 360.0) * state['radius_step']
    
    # Check if we've exceeded max radius
    if current_radius > state['max_radius']:
        state['complete'] = True
        print("Spiral complete!")
        return
    
    # Calculate current target position on spiral
    angle_rad = np.radians(state['current_angle_deg'])
    target_x = state['start_x'] + current_radius * np.sin(angle_rad)
    target_y = state['start_y'] + current_radius * np.cos(angle_rad)
    
    # Calculate distance to target
    dx = target_x - robot.x
    dy = target_y - robot.y
    distance_to_target = np.sqrt(dx**2 + dy**2)
    
    # If we're close to the current target, increment angle to get next waypoint
    # Use a dynamic threshold based on radius to avoid getting stuck
    threshold = max(0.15, current_radius * 0.05)  # 5% of radius or 15cm minimum
    
    if distance_to_target < threshold:
        # Move to next waypoint
        state['current_angle_deg'] += state['angle_step_deg']
        
        # Recalculate target for new angle
        current_radius = (state['current_angle_deg'] / 360.0) * state['radius_step']
        if current_radius > state['max_radius']:
            state['complete'] = True
            return
        
        angle_rad = np.radians(state['current_angle_deg'])
        target_x = state['start_x'] + current_radius * np.sin(angle_rad)
        target_y = state['start_y'] + current_radius * np.cos(angle_rad)
        dx = target_x - robot.x
        dy = target_y - robot.y
    
    # Calculate heading toward target
    if abs(dx) > 0.001 or abs(dy) > 0.001:
        target_heading = np.degrees(np.arctan2(dx, dy))
        
        # Calculate angle difference (normalized to [-180, 180])
        angle_diff = target_heading - robot.heading
        while angle_diff > 180:
            angle_diff -= 360
        while angle_diff < -180:
            angle_diff += 360
        
        # Smooth turning with rate limit
        max_turn = 180 * time_step  # 180 deg/sec - faster turning
        if abs(angle_diff) > max_turn:
            robot.turn(np.sign(angle_diff) * max_turn)
        else:
            robot.set_heading(target_heading)
    
    # Always move forward
    robot.move_forward(robot.speed * time_step)




    


def run_demo():
    """Run visualization with custom algorithm."""
    # Setup
    environment = SearchEnvironment(
        radius=config.SEARCH_RADIUS,
        grid_size=config.GRID_SIZE
    )
    
    robot = SearchRobot(
        start_x=0, start_y=0,
        speed=config.ROBOT_SPEED,
        fov_h=config.CAMERA_FOV_HORIZONTAL,
        fov_v=config.CAMERA_FOV_VERTICAL,
        camera_range=config.CAMERA_MAX_RANGE
    )
    
    robot.set_search_algorithm(my_custom_algorithm)
    visualizer = SearchVisualizer(environment, robot)
    
    # Add space for slider at bottom
    visualizer.fig.subplots_adjust(bottom=0.15)
    
    # Create speed slider
    ax_slider = visualizer.fig.add_axes([0.25, 0.05, 0.5, 0.03])
    speed_slider = Slider(
        ax=ax_slider,
        label='Speed',
        valmin=0.1,
        valmax=5.0,
        valinit=1.0,
        valstep=0.1
    )
    
    # Store simulation speed multiplier
    sim_speed = {'multiplier': 1.0}
    
    def update_speed(val):
        sim_speed['multiplier'] = val
    
    speed_slider.on_changed(update_speed)
    
    # Animation loop
    def animate(frame):
        # Run multiple steps based on speed multiplier
        steps = int(sim_speed['multiplier'])
        fraction = sim_speed['multiplier'] - steps
        
        for _ in range(steps):
            robot.step(config.TIME_STEP)
            _update_coverage(robot, environment)
        
        # Handle fractional step
        if fraction > 0 and np.random.random() < fraction:
            robot.step(config.TIME_STEP)
            _update_coverage(robot, environment)
        
        visualizer.update(frame)
        
        return visualizer.ax_2d, visualizer.ax_3d
    
    print("🚀 Running custom algorithm demo...")
    print("📝 Edit my_custom_algorithm() in demo.py to test your own algorithm!")
    print("🎚️  Use the slider at the bottom to adjust simulation speed!\n")
    
    anim = FuncAnimation(
        visualizer.fig, animate,
        frames=2000, interval=config.UPDATE_INTERVAL,
        blit=False, repeat=False
    )
    
    plt.show()
    
    print(f"\n✅ Final coverage: {environment.get_coverage_percentage():.1f}%")


def _update_coverage(robot, environment):
    """Helper function to update coverage based on robot's camera view."""
    visible_cells = set()
    heading_rad = np.radians(robot.heading)
    fov_rad = np.radians(config.CAMERA_FOV_HORIZONTAL)
    half_fov = fov_rad / 2
    
    for angle_offset in np.linspace(-half_fov, half_fov, 30):
        direction_angle = heading_rad + angle_offset
        for distance in np.linspace(config.CAMERA_MIN_RANGE, config.CAMERA_MAX_RANGE, 20):
            px = robot.x + distance * np.sin(direction_angle)
            py = robot.y + distance * np.cos(direction_angle)
            grid_x, grid_y = environment.world_to_grid(px, py)
            if environment.is_within_bounds(grid_x, grid_y):
                visible_cells.add((grid_x, grid_y))
    
    environment.mark_cells_as_seen(visible_cells)


if __name__ == "__main__":
    run_demo()
