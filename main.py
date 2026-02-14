"""Main entry point for URC robot search visualization."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider

from environment import SearchEnvironment
from robot import SearchRobot
from visualizer import SearchVisualizer
import config


# =============================================================================
# EXAMPLE SEARCH ALGORITHMS - Replace these with your own!
# =============================================================================

def spiral_search(robot: SearchRobot, time_step: float):
    """
    Spiral search pattern - robot moves in an expanding spiral.
    """
    # Simple spiral: move forward and gradually turn
    robot.move_forward(robot.speed * time_step)
    robot.turn(2)  # Turn 2 degrees per step


def lawnmower_search(robot: SearchRobot, time_step: float):
    """
    Lawnmower/boustrophedon search pattern - back and forth coverage.
    """
    # This is a simple version - you'd want to track state for real implementation
    if not hasattr(robot, '_lawnmower_state'):
        robot._lawnmower_state = {'direction': 0, 'distance': 0, 'row': 0}
    
    state = robot._lawnmower_state
    distance_moved = robot.speed * time_step
    state['distance'] += distance_moved
    
    # Move in rows
    row_length = 8  # meters
    if state['distance'] >= row_length:
        # Turn and move to next row
        robot.turn(90)
        robot.move_forward(1.0)
        robot.turn(90)
        state['distance'] = 0
        state['row'] += 1


def expanding_square_search(robot: SearchRobot, time_step: float):
    """
    Expanding square search pattern.
    """
    if not hasattr(robot, '_square_state'):
        robot._square_state = {'side_length': 1, 'current_distance': 0, 'sides_completed': 0}
    
    state = robot._square_state
    distance_moved = robot.speed * time_step
    state['current_distance'] += distance_moved
    robot.move_forward(distance_moved)
    
    if state['current_distance'] >= state['side_length']:
        robot.turn(90)
        state['sides_completed'] += 1
        state['current_distance'] = 0
        
        # Expand square after every 2 sides
        if state['sides_completed'] % 2 == 0:
            state['side_length'] += 0.5


def random_walk_search(robot: SearchRobot, time_step: float):
    """
    Random walk search - explores randomly.
    """
    if not hasattr(robot, '_random_state'):
        robot._random_state = {'steps_in_direction': 0}
    
    state = robot._random_state
    
    if state['steps_in_direction'] <= 0:
        # Choose new random direction
        robot.turn(np.random.uniform(-180, 180))
        state['steps_in_direction'] = np.random.randint(10, 30)
    
    robot.move_forward(robot.speed * time_step)
    state['steps_in_direction'] -= 1


def star_pattern_search(robot: SearchRobot, time_step: float):
    """
    Star pattern - moves outward in rays from center.
    """
    if not hasattr(robot, '_star_state'):
        robot._star_state = {'angle': 0, 'radius': 0, 'expanding': True}
    
    state = robot._star_state
    
    if state['expanding']:
        robot.move_forward(robot.speed * time_step)
        state['radius'] += robot.speed * time_step
        
        if state['radius'] >= 4:  # Max radius
            state['expanding'] = False
            robot.set_heading(state['angle'] + 45)  # Next ray
            state['angle'] += 45
            state['radius'] = 0
    else:
        # Return to center
        robot.set_heading(state['angle'] + 180)
        robot.move_forward(robot.speed * time_step)
        state['radius'] -= robot.speed * time_step
        
        if state['radius'] <= 0:
            state['expanding'] = True


# =============================================================================
# MAIN SIMULATION
# =============================================================================

def run_simulation(search_algorithm):
    """
    Run the URC search visualization.
    
    Args:
        search_algorithm: Function that takes (robot, time_step) and updates robot
    """
    print("=" * 60)
    print("URC ROBOT SEARCH VISUALIZATION")
    print("=" * 60)
    
    # Create environment
    print(f"\n📍 Creating search environment...")
    print(f"   Search radius: {config.SEARCH_RADIUS}m")
    print(f"   Grid size: {config.GRID_SIZE}m ({config.GRID_CELLS}x{config.GRID_CELLS} cells)")
    
    environment = SearchEnvironment(
        radius=config.SEARCH_RADIUS,
        grid_size=config.GRID_SIZE
    )
    
    # Create robot with RealSense D435 specs
    print(f"\n🤖 Initializing robot...")
    print(f"   Camera: Intel RealSense D435")
    print(f"   FOV: {config.CAMERA_FOV_HORIZONTAL}° × {config.CAMERA_FOV_VERTICAL}°")
    print(f"   Range: {config.CAMERA_MAX_RANGE}m")
    print(f"   Speed: {config.ROBOT_SPEED}m/s")
    
    robot = SearchRobot(
        start_x=config.ROBOT_START_POS[0],
        start_y=config.ROBOT_START_POS[1],
        speed=config.ROBOT_SPEED,
        fov_h=config.CAMERA_FOV_HORIZONTAL,
        fov_v=config.CAMERA_FOV_VERTICAL,
        camera_range=config.CAMERA_MAX_RANGE
    )
    
    # Set search algorithm
    robot.set_search_algorithm(search_algorithm)
    print(f"   Algorithm: {search_algorithm.__name__}")
    
    # Create visualizer
    print(f"\n🎨 Setting up visualization...")
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
    
    # Animation function
    def animate(frame):
        # Run multiple steps based on speed multiplier
        steps = int(sim_speed['multiplier'])
        fraction = sim_speed['multiplier'] - steps
        
        for _ in range(steps):
            # Execute search algorithm step
            robot.step(config.TIME_STEP)
            
            # Calculate visible cells and mark as seen
            visible_cells = set()
            heading_rad = np.radians(robot.heading)
            fov_rad = np.radians(config.CAMERA_FOV_HORIZONTAL)
            half_fov = fov_rad / 2
            
            # Sample points in FOV cone
            for angle_offset in np.linspace(-half_fov, half_fov, 30):
                direction_angle = heading_rad + angle_offset
                for distance in np.linspace(config.CAMERA_MIN_RANGE, config.CAMERA_MAX_RANGE, 20):
                    px = robot.x + distance * np.sin(direction_angle)
                    py = robot.y + distance * np.cos(direction_angle)
                    
                    # Convert to grid coordinates
                    grid_x, grid_y = environment.world_to_grid(px, py)
                    if environment.is_within_bounds(grid_x, grid_y):
                        visible_cells.add((grid_x, grid_y))
            
            # Mark cells as seen
            environment.mark_cells_as_seen(visible_cells)
        
        # Handle fractional step
        if fraction > 0 and np.random.random() < fraction:
            robot.step(config.TIME_STEP)
            # (Coverage update for fractional step - simplified)
        
        # Update visualization
        visualizer.update(frame)
        
        # Print progress every 50 frames
        if frame % 50 == 0 and frame > 0:
            coverage = environment.get_coverage_percentage()
            print(f"   Frame {frame}: Coverage {coverage:.1f}%")
        
        return visualizer.ax_2d, visualizer.ax_3d
    
    # Start simulation
    print(f"\n▶️  Starting simulation...")
    print("   🎚️  Use the slider at the bottom to adjust speed!")
    print("   Close the window to stop.\n")
    
    anim = FuncAnimation(
        visualizer.fig,
        animate,
        frames=2000,
        interval=config.UPDATE_INTERVAL,
        blit=False,
        repeat=False
    )
    
    plt.show()
    
    # Final statistics
    final_coverage = environment.get_coverage_percentage()
    print(f"\n📊 Final Statistics:")
    print(f"   Coverage: {final_coverage:.1f}%")
    print(f"   Path length: {len(robot.path)} points")
    print(f"   Distance traveled: ~{len(robot.path) * robot.speed * config.TIME_STEP:.1f}m")


if __name__ == "__main__":
    # Choose which search algorithm to run
    ALGORITHMS = {
        '1': ('Spiral Search', spiral_search),
        '2': ('Lawnmower Search', lawnmower_search),
        '3': ('Expanding Square', expanding_square_search),
        '4': ('Random Walk', random_walk_search),
        '5': ('Star Pattern', star_pattern_search),
    }
    
    print("\n🔍 Available Search Algorithms:")
    for key, (name, _) in ALGORITHMS.items():
        print(f"   {key}. {name}")
    
    choice = input("\nSelect algorithm (1-5) [default: 1]: ").strip() or '1'
    
    if choice in ALGORITHMS:
        name, algorithm = ALGORITHMS[choice]
        print(f"\n✓ Selected: {name}\n")
        run_simulation(algorithm)
    else:
        print("Invalid choice. Using Spiral Search.")
        run_simulation(spiral_search)
