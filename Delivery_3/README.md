# Delivery 3 — Gazebo Leader/Follower (Option B)

## Overview

Two differential-drive cars in Gazebo: a **leader** drives in circles, a **follower** tracks its position via world-frame poses and steers toward it using proportional control.

## Screen Recording

**[Loom Video Demo](https://www.loom.com/share/5f0250b083cf4be9bbf78da59ba91406)**

## Run Commands

```bash
source /opt/ros/jazzy/setup.bash
cd Delivery_3
colcon build --cmake-args -DPython3_EXECUTABLE=/usr/bin/python3
source install/setup.bash

# Launch everything at once
ros2 launch gazebo_follower gazebo_follower.launch.py
```

### Step-by-step (alternative)

```bash
# Terminal 1 — Gazebo
gz sim empty_class3.sdf

# Terminal 2 — Spawn cars
ros2 run ros_gz_sim create -entity leader_car -file leader_car.urdf -x 0 -y 0 -z 0.2
ros2 run ros_gz_sim create -entity follower_car -file follower_car.urdf -x -3 -y 0 -z 0.2

# Terminal 3 — Bridges (ROS ↔ Gazebo)
ros2 run ros_gz_bridge parameter_bridge /leader/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist &
ros2 run ros_gz_bridge parameter_bridge /follower/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist &
ros2 run ros_gz_bridge parameter_bridge '/world/empty_class3/dynamic_pose/info@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V' &

# Terminal 4 — Leader (drives in circle)
ros2 run gazebo_follower leader_node

# Terminal 5 — Follower (follows leader)
ros2 run gazebo_follower follower_node
```

## Source Code

| File | Role |
|------|------|
| `src/gazebo_follower/gazebo_follower/leader_node.py` | Publisher — sends constant Twist to `/leader/cmd_vel` (circle pattern) |
| `src/gazebo_follower/gazebo_follower/follower_node.py` | Subscriber — reads world poses, computes heading error, publishes to `/follower/cmd_vel` |
| `src/gazebo_follower/launch/gazebo_follower.launch.py` | Launch file — starts Gazebo, spawns cars, bridges, and both nodes |
| `leader_car.urdf` / `follower_car.urdf` | URDF models with DiffDrive plugin on separate cmd_vel topics |

## What Changed from Turtlesim to Gazebo

In turtlesim the follower used the built-in TF tree (`lookup_transform`) to find the leader's position relative to itself and drive toward it — all communication stayed inside ROS. In Gazebo there is no shared TF tree between the two cars; instead, each car is controlled by a DiffDrive plugin that listens to its own `cmd_vel` topic inside the Gazebo transport layer. To get positions, the follower subscribes to the Gazebo world's `dynamic_pose/info` topic (bridged to ROS as a `TFMessage` via `ros_gz_bridge`), which provides absolute world-frame poses for every entity. The follower then computes the angle and distance to the leader in the world frame and applies the same proportional controller (linear speed ∝ distance, angular speed ∝ heading error). The core control logic is identical to the turtlesim version, but the data path changed from direct ROS topics to a Gazebo → bridge → ROS → bridge → Gazebo round-trip.
