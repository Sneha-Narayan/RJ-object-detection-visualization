# Custom Search Algorithms for URC Visualization

This file shows you how to create your own search algorithms for the visualization.

## How Search Functions Work

A search algorithm is a Python function with this signature:

```python
def my_search_algorithm(robot: SearchRobot, time_step: float):
    """
    Your search algorithm function.
    
    Args:
        robot: The SearchRobot instance you can control
        time_step: Time elapsed since last call (in seconds)
    """
    # Your algorithm logic here
    robot.move_forward(1.0)
    robot.turn(45)
```

## Robot Control Methods

The `robot` object has these methods:

### Movement
- `robot.move_forward(distance)` - Move forward in current heading direction
- `robot.move(dx, dy)` - Move by relative x, y distance
- `robot.turn(angle_degrees)` - Turn by angle (positive = clockwise)
- `robot.set_heading(angle_degrees)` - Set absolute heading (0 = North, 90 = East)

### State Access
- `robot.x, robot.y` - Current position
- `robot.heading` - Current heading in degrees
- `robot.speed` - Robot speed in m/s
- `robot.path` - List of (x, y) positions visited
- `robot.camera_range` - Camera range (3m for RealSense D435)
- `robot.fov_horizontal` - Horizontal FOV (87° for RealSense D435)

### State Storage
You can store algorithm state on the robot object:
```python
if not hasattr(robot, '_my_state'):
    robot._my_state = {'counter': 0, 'phase': 'searching'}

state = robot._my_state
state['counter'] += 1
```

## Example: Grid Search Algorithm

```python
def grid_search(robot: SearchRobot, time_step: float):
    """
    Systematic grid search covering the entire area.
    """
    if not hasattr(robot, '_grid_state'):
        robot._grid_state = {
            'row': 0,
            'distance_in_row': 0,
            'row_spacing': 2.5,  # spacing between rows
            'moving_right': True
        }
    
    state = robot._grid_state
    move_distance = robot.speed * time_step
    
    # Move along current row
    state['distance_in_row'] += move_distance
    robot.move_forward(move_distance)
    
    # Check if we've reached the end of the row
    if state['distance_in_row'] >= 18:  # near edge of 10m radius
        # Move to next row
        state['row'] += 1
        state['distance_in_row'] = 0
        
        # Turn around and shift to next row
        robot.turn(90)
        robot.move_forward(state['row_spacing'])
        robot.turn(90)
        state['moving_right'] = not state['moving_right']
```

## Example: Camera-Optimized Search

```python
def camera_optimized_search(robot: SearchRobot, time_step: float):
    """
    Search pattern optimized for camera FOV coverage.
    
    Uses the 87° FOV to minimize overlap and maximize coverage.
    """
    if not hasattr(robot, '_camera_state'):
        # Calculate optimal spacing based on camera FOV
        fov_rad = np.radians(robot.fov_horizontal)
        optimal_spacing = 2 * robot.camera_range * np.tan(fov_rad / 2)
        
        robot._camera_state = {
            'sweep_angle': 0,
            'radius': 1,
            'spacing': optimal_spacing * 0.8,  # 80% for overlap
            'sweeping': True
        }
    
    state = robot._camera_state
    
    if state['sweeping']:
        # Sweep in a circle at current radius
        angular_speed = 30  # degrees per second
        robot.turn(angular_speed * time_step)
        state['sweep_angle'] += angular_speed * time_step
        
        if state['sweep_angle'] >= 360:
            # Complete sweep, move to next radius
            state['sweep_angle'] = 0
            state['radius'] += state['spacing']
            state['sweeping'] = False
    else:
        # Move outward to next sweep radius
        robot.move_forward(robot.speed * time_step)
        if robot.x**2 + robot.y**2 >= state['radius']**2:
            state['sweeping'] = True
```

## Example: Target-Aware Search

```python
def target_aware_search(robot: SearchRobot, time_step: float):
    """
    Search that can be guided toward likely target locations.
    """
    if not hasattr(robot, '_target_state'):
        # Define areas of interest (e.g., from competition hints)
        robot._target_state = {
            'interest_points': [(5, 5), (-3, 7), (2, -6)],
            'current_target_idx': 0,
            'search_radius': 2.0,
            'circling': False,
            'circle_angle': 0
        }
    
    state = robot._target_state
    
    # Get current target point
    if state['current_target_idx'] < len(state['interest_points']):
        target_x, target_y = state['interest_points'][state['current_target_idx']]
        
        # Calculate distance to target
        dx = target_x - robot.x
        dy = target_y - robot.y
        distance = np.sqrt(dx**2 + dy**2)
        
        if distance > state['search_radius']:
            # Move toward target
            target_angle = np.degrees(np.arctan2(dx, dy))
            robot.set_heading(target_angle)
            robot.move_forward(robot.speed * time_step)
        else:
            # Circle around target area
            if not state['circling']:
                state['circling'] = True
            
            robot.turn(30 * time_step)  # Circle
            robot.move_forward(robot.speed * time_step * 0.5)
            state['circle_angle'] += 30 * time_step
            
            if state['circle_angle'] >= 720:  # Two full circles
                # Move to next target
                state['current_target_idx'] += 1
                state['circling'] = False
                state['circle_angle'] = 0
    else:
        # All targets searched, do random exploration
        robot.turn(np.random.uniform(-30, 30))
        robot.move_forward(robot.speed * time_step)
```

## Using Your Custom Algorithm

1. Define your function in `main.py` or in this file
2. Import it if needed
3. Pass it to `run_simulation()`:

```python
from search_algorithms import my_custom_search

run_simulation(my_custom_search)
```

Or add it to the ALGORITHMS dictionary in main.py:

```python
ALGORITHMS = {
    '1': ('Spiral Search', spiral_search),
    '2': ('My Custom Search', my_custom_search),  # Add here
    # ...
}
```

## Tips for Effective Search Algorithms

1. **Use the camera specs**: The RealSense D435 has 3m range and 87° FOV
2. **Avoid redundant coverage**: Track where you've been
3. **Consider edge cases**: Stay within the 10m search radius
4. **Optimize for time**: URC has time limits
5. **Handle obstacles**: Real environment will have terrain
6. **Test different speeds**: Adjust `config.ROBOT_SPEED`

## Debugging Your Algorithm

Add print statements to see what's happening:

```python
def debug_search(robot: SearchRobot, time_step: float):
    if not hasattr(robot, '_debug_counter'):
        robot._debug_counter = 0
    
    robot._debug_counter += 1
    
    if robot._debug_counter % 100 == 0:
        print(f"Position: ({robot.x:.2f}, {robot.y:.2f}), "
              f"Heading: {robot.heading:.0f}°")
    
    # Your algorithm logic
    robot.move_forward(robot.speed * time_step)
```

## Performance Metrics to Track

- **Coverage percentage**: How much area seen
- **Time to full coverage**: Frames or seconds
- **Path efficiency**: Distance traveled vs area covered
- **Redundancy**: How much area is seen multiple times
