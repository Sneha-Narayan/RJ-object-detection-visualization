"""Configuration parameters for URC robot search visualization."""

# Search area settings
SEARCH_RADIUS = 10.0  # meters (10m radius given by URC)
GRID_SIZE = 0.5  # meters (size of each grid square)
GRID_CELLS = int((SEARCH_RADIUS * 2) / GRID_SIZE)  # 40x40 grid

# Robot settings
ROBOT_START_POS = (0, 0)  # Start at center (relative coordinates)
ROBOT_SPEED = 1.0  # meters per second

# Intel RealSense D435 Camera specifications
CAMERA_FOV_HORIZONTAL = 87  # degrees
CAMERA_FOV_VERTICAL = 58  # degrees
CAMERA_MAX_RANGE = 3.0  # meters (ideal range)
CAMERA_MIN_RANGE = 0.3  # meters (minimum range)

# Simulation settings
TIME_STEP = 0.1  # seconds per step
UPDATE_INTERVAL = 50  # milliseconds between visualization updates

# Visualization settings
SHOW_ROBOT_PATH = True
SHOW_FOV_CONE = True
UNSEEN_COLOR = 'black'
SEEN_COLOR = 'green'
ROBOT_COLOR = 'red'
