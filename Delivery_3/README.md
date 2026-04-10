# Delivery 3 — Gazebo Leader/Follower (Option B)

## Overview

Two-robot follower behavior from Exercise 2 (leader + follower) reproduced in Gazebo, bridged through ROS 2 topics.

## Run Commands

```bash
source /opt/ros/jazzy/setup.bash
cd Delivery_3
colcon build --cmake-args -DPython3_EXECUTABLE=/usr/bin/python3
source install/setup.bash

# Option 1: Launch everything at once
ros2 launch gazebo_follower gazebo_follower.launch.py

# Option 2: Step-by-step
# Terminal 1 — Gazebo server
gz sim empty_class3.sdf

# Terminal 2 — Spawn cars
ros2 run ros_gz_sim create -entity leader_car -file leader_car.urdf -x 0 -y 0 -z 0.2
ros2 run ros_gz_sim create -entity follower_car -file follower_car.urdf -x -3 -y 0 -z 0.2

# Terminal 3 — Bridges (ROS ↔ Gazebo)
ros2 run ros_gz_bridge parameter_bridge /leader/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist
ros2 run ros_gz_bridge parameter_bridge /follower/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist
ros2 run ros_gz_bridge parameter_bridge '/model/leader_car/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry'
ros2 run ros_gz_bridge parameter_bridge '/model/follower_car/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry'

# Terminal 4 — Leader (drives in circle)
ros2 run gazebo_follower leader_node

# Terminal 5 — Follower (follows leader)
ros2 run gazebo_follower follower_node
```

## What I Did and What Changed from Turtlesim to Gazebo

In turtlesim, the follower used the built-in TF tree (`lookup_transform`) to find the leader's position relative to itself and drive toward it. In Gazebo, there is no built-in TF tree — instead, each car's DiffDrive plugin produces an `/model/<name>/odometry` topic inside Gazebo, which is bridged to ROS 2 using `ros_gz_bridge`. The follower node subscribes to both the leader's and its own odometry, computes the relative angle and distance in the global frame, and publishes velocity commands to `/follower/cmd_vel` which is bridged back into Gazebo. The core proportional control logic (linear speed proportional to distance, angular speed proportional to heading error) remains the same as the turtlesim version, but the communication path changed from direct ROS topics to Gazebo → bridge → ROS → bridge → Gazebo.
