#!/usr/bin/env python3
"""
Test script to verify the visualization components work correctly.
Run this to test without opening the GUI.
"""

import numpy as np
from environment import SearchEnvironment
from robot import SearchRobot
import config


def test_environment():
    """Test environment setup and grid operations."""
    print("Testing SearchEnvironment...")
    
    env = SearchEnvironment(radius=10.0, grid_size=0.5)
    assert env.radius == 10.0
    assert env.grid_size == 0.5
    assert env.grid_cells == 40
    
    # Test coordinate conversion
    grid_x, grid_y = env.world_to_grid(0, 0)  # Center
    assert grid_x == 20 and grid_y == 20, f"Center conversion failed: {grid_x}, {grid_y}"
    
    world_x, world_y = env.grid_to_world(20, 20)
    assert abs(world_x) < 0.5 and abs(world_y) < 0.5, "Reverse conversion failed"
    
    # Test boundary checking
    assert env.is_within_search_area(0, 0), "Center should be in bounds"
    assert not env.is_within_search_area(15, 15), "Far corner should be out of bounds"
    
    # Test coverage
    assert env.get_coverage_percentage() == 0.0, "Initial coverage should be 0"
    
    env.mark_cells_as_seen({(20, 20)})
    assert env.get_coverage_percentage() > 0, "Coverage should increase"
    
    print("✓ SearchEnvironment tests passed\n")


def test_robot():
    """Test robot movement and control."""
    print("Testing SearchRobot...")
    
    robot = SearchRobot(
        start_x=0, start_y=0, speed=1.0,
        fov_h=87, fov_v=58, camera_range=3.0
    )
    
    # Test initial state
    assert robot.x == 0 and robot.y == 0, "Robot should start at origin"
    assert robot.heading == 0, "Initial heading should be 0"
    
    # Test movement
    robot.move_forward(1.0)
    assert abs(robot.y - 1.0) < 0.01, f"Robot should move forward: y={robot.y}"
    assert abs(robot.x) < 0.01, f"Robot should not move sideways: x={robot.x}"
    
    # Test turning
    robot.set_heading(90)
    assert robot.heading == 90, "Heading should be 90"
    
    robot.move_forward(1.0)
    assert abs(robot.x - 1.0) < 0.01, f"Robot should move east: x={robot.x}"
    
    # Test turn
    robot.turn(45)
    assert robot.heading == 135, f"Heading should be 135, got {robot.heading}"
    
    # Test path tracking
    assert len(robot.path) > 2, "Robot should track path"
    
    print("✓ SearchRobot tests passed\n")


def test_integration():
    """Test robot and environment integration."""
    print("Testing integration...")
    
    env = SearchEnvironment(radius=10.0, grid_size=0.5)
    robot = SearchRobot(0, 0, 1.0, 87, 58, 3.0)
    
    # Simulate some movement
    for _ in range(10):
        robot.move_forward(0.5)
        robot.turn(36)  # 10 steps = full circle
    
    # Calculate visible cells (simplified)
    heading_rad = np.radians(robot.heading)
    fov_rad = np.radians(robot.fov_horizontal)
    visible = set()
    
    for angle_offset in np.linspace(-fov_rad/2, fov_rad/2, 10):
        for dist in np.linspace(0, robot.camera_range, 10):
            px = robot.x + dist * np.sin(heading_rad + angle_offset)
            py = robot.y + dist * np.cos(heading_rad + angle_offset)
            gx, gy = env.world_to_grid(px, py)
            if env.is_within_bounds(gx, gy):
                visible.add((gx, gy))
    
    env.mark_cells_as_seen(visible)
    coverage = env.get_coverage_percentage()
    
    assert coverage > 0, "Robot should have seen some area"
    assert coverage < 100, "Robot shouldn't have seen everything in 10 steps"
    
    print(f"✓ Integration test passed (coverage: {coverage:.1f}%)\n")


def test_config():
    """Test configuration values."""
    print("Testing configuration...")
    
    assert config.SEARCH_RADIUS == 10.0, "Search radius should be 10m"
    assert config.GRID_SIZE == 0.5, "Grid size should be 0.5m"
    assert config.CAMERA_FOV_HORIZONTAL == 87, "FOV should be 87°"
    assert config.CAMERA_MAX_RANGE == 3.0, "Camera range should be 3m"
    
    print("✓ Configuration tests passed\n")


if __name__ == "__main__":
    print("=" * 60)
    print("URC ROBOT SEARCH VISUALIZATION - TEST SUITE")
    print("=" * 60)
    print()
    
    try:
        test_config()
        test_environment()
        test_robot()
        test_integration()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYou can now run:")
        print("  python main.py      - Interactive algorithm selector")
        print("  python demo.py      - Quick demo with custom algorithm")
        print()
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
