# Delivery 4 — FSM Robot (Exercise 7, Session 4)

## Run Commands

```bash
source /opt/ros/jazzy/setup.bash
cd Delivery_4/ros2_ws
colcon build --packages-select robot_description
source install/setup.bash

# Terminal 1 — Gazebo with red sphere world
ros2 launch robot_description red_sphere_world.launch.py

# Terminal 2 — Spawn robot (includes sensors: LiDAR, IMU, Camera)
ros2 launch robot_description spawn.launch.py

# Terminal 3 — ROS ↔ Gazebo bridges
ros2 launch robot_description bridge.launch.py

# Terminal 4 — FSM node
ros2 run robot_description fsm_robot
```

## FSM Explanation

The `fsm_robot.py` node implements a finite state machine with four states that reacts to three sensors (LiDAR, Camera, IMU). It starts in **EXPLORE**, where the robot rotates in place searching for a red object. When the camera detects a red blob (via HSV colour thresholding) larger than 500 pixels, it transitions to **TRACK** and drives toward the red object using proportional steering based on the centroid's offset from the image centre. If the LiDAR detects an obstacle closer than 0.6 m in any state, the robot enters **AVOID** and rotates in place until the nearest reading exceeds 1.0 m, then returns to EXPLORE. At any time, if the IMU detects a gyroscope spike (> 3.0 rad/s) or excessive tilt (> 0.5 rad roll/pitch), the robot enters **STOP** and halts until the anomaly clears. The state transitions are logged by the node and can be observed in the terminal output.
