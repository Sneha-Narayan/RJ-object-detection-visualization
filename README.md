# URC Robot Search Visualization

A Python visualization tool for designing and testing robot search algorithms for the University Rover Challenge (URC) competition.

## Overview

In the URC competition, you're given approximate target coordinates (within a 10m radius) and must search that area. This tool helps you:
- Visualize different search algorithms in real-time
- See coverage maps showing searched vs unsearched areas
- Test with realistic camera specifications (Intel RealSense D435)
- Optimize your search patterns before field testing

## Features

- **Dual visualization**: 2D top-down and 3D perspective views
- **Grid-based coverage**: Black squares (unseen) turn green (seen) as robot explores
- **Realistic camera FOV**: 87° × 58° field of view, 3m ideal range
- **10m search radius**: Matches URC competition specs
- **Pluggable algorithms**: Easy to add your own search functions
- **Coverage metrics**: Track percentage of area covered in real-time

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```bash
python main.py
```

Select a search algorithm when prompted and watch it visualize!

## Creating Your Own Search Algorithm

Search algorithms are simple Python functions. Example:

```python
def my_search(robot: SearchRobot, time_step: float):
    """My custom search algorithm."""
    robot.move_forward(robot.speed * time_step)
    robot.turn(5)  # Turn 5 degrees each step
```

See `search_algorithms.py` for detailed examples and documentation.

## Built-in Search Algorithms

1. **Spiral Search** - Expanding spiral from center
2. **Lawnmower Search** - Back-and-forth rows
3. **Expanding Square** - Growing square pattern
4. **Random Walk** - Randomized exploration
5. **Star Pattern** - Radial rays from center

## Robot Control API

### Movement
- `robot.move_forward(distance)` - Move forward
- `robot.turn(angle)` - Turn (positive = clockwise)
- `robot.set_heading(angle)` - Set absolute heading

### State
- `robot.x, robot.y` - Current position
- `robot.heading` - Current heading (0° = North)
- `robot.camera_range` - Camera range (3m)
- `robot.fov_horizontal` - Field of view (87°)

## Configuration

Edit `config.py` to adjust:
- Search radius (default: 10m)
- Grid size (default: 0.5m squares)
- Robot speed (default: 1.0 m/s)
- Camera specifications
- Visualization settings

## Camera Specifications

**Intel RealSense D435**
- Horizontal FOV: 87°
- Vertical FOV: 58°
- Ideal range: 0.3m - 3m
- The visualization uses these real specs for accurate field-of-view

## Understanding the Visualization

### 2D View (Left)
- **Black squares**: Unseen areas
- **Green squares**: Areas the robot has seen
- **Red circle**: Robot position
- **White arrow**: Robot heading
- **Cyan wedge**: Camera field of view
- **Yellow line**: Robot's path

### 3D View (Right)
- **Black/flat squares**: Unseen (height: 0.05m)
- **Green/raised squares**: Seen (height: 0.1m)
- **Red cone**: Robot with heading indicator
- **Cyan cylinder**: Search boundary

## Project Structure

```
visualization/
├── main.py              # Entry point with example algorithms
├── robot.py             # Robot class with movement and control
├── environment.py       # Search environment and coverage tracking
├── visualizer.py        # 2D and 3D visualization
├── config.py            # Configuration parameters
├── search_algorithms.py # Algorithm examples and documentation
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Tips for Algorithm Development

1. **Test incrementally**: Start simple, add complexity
2. **Use the camera specs**: 3m range, 87° FOV
3. **Optimize coverage**: Minimize overlap, maximize new areas
4. **Consider efficiency**: Time matters in competition
5. **Handle boundaries**: Stay within 10m radius
6. **Track state**: Use robot attributes to store algorithm state

## Example: Adding Your Algorithm

```python
# In main.py, add your algorithm function:

def my_custom_search(robot: SearchRobot, time_step: float):
    """Your algorithm description."""
    # Your logic here
    robot.move_forward(1.0)

# Then add to the ALGORITHMS dictionary:
ALGORITHMS = {
    '1': ('Spiral Search', spiral_search),
    '2': ('My Custom Search', my_custom_search),  # Add here
    # ...
}
```

## Performance Metrics

The visualization displays:
- **Coverage %**: Percentage of search area seen
- **Position**: Current robot coordinates
- **Heading**: Current robot direction
- **Path**: Visual trail of robot movement

## Advanced Usage

### Saving Algorithm State

```python
def stateful_search(robot: SearchRobot, time_step: float):
    if not hasattr(robot, '_my_state'):
        robot._my_state = {'phase': 1, 'counter': 0}
    
    state = robot._my_state
    # Use state in your algorithm
```

### Accessing Environment Info

```python
# In your algorithm, you can check boundaries:
distance_from_center = np.sqrt(robot.x**2 + robot.y**2)
if distance_from_center > 9:  # Near edge
    robot.set_heading(np.degrees(np.arctan2(-robot.x, -robot.y)))
```

## Troubleshooting

**Visualization is slow**: Reduce `UPDATE_INTERVAL` in config.py or grid resolution
**Robot leaves boundary**: Add boundary checking in your algorithm
**Coverage seems wrong**: Check camera FOV calculations match your expectations

## For URC Competition

This tool is specifically designed for URC search tasks where:
- You receive approximate target coordinates
- Search area is within 10m radius
- You need efficient coverage patterns
- Time optimization matters
- Camera specifications are critical

Good luck with your URC competition! 🚀
