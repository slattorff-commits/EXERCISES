"""Launch file for Gazebo leader/follower demo.

Steps performed:
1. Start Gazebo with the empty world
2. Spawn leader_car and follower_car
3. Bridge Gazebo pose → ROS TF and cmd_vel topics
4. Start leader and follower nodes
"""
import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node


# Resolve paths relative to this launch file
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_DELIVERY_DIR = os.path.dirname(_THIS_DIR)  # gazebo_follower pkg
_ROOT_DIR = os.path.dirname(os.path.dirname(_DELIVERY_DIR))  # Delivery_3 root


def generate_launch_description():
    world_file = os.path.join(_ROOT_DIR, 'empty_class3.sdf')
    leader_urdf = os.path.join(_ROOT_DIR, 'leader_car.urdf')
    follower_urdf = os.path.join(_ROOT_DIR, 'follower_car.urdf')

    # 1. Start Gazebo simulator
    gz_sim = ExecuteProcess(
        cmd=['gz', 'sim', world_file],
        output='screen',
    )

    # 2. Spawn leader car at origin
    spawn_leader = TimerAction(
        period=4.0,
        actions=[
            ExecuteProcess(
                cmd=[
                    'ros2', 'run', 'ros_gz_sim', 'create',
                    '-entity', 'leader_car',
                    '-file', leader_urdf,
                    '-x', '0', '-y', '0', '-z', '0.2',
                ],
                output='screen',
            )
        ],
    )

    # 3. Spawn follower car behind leader
    spawn_follower = TimerAction(
        period=6.0,
        actions=[
            ExecuteProcess(
                cmd=[
                    'ros2', 'run', 'ros_gz_sim', 'create',
                    '-entity', 'follower_car',
                    '-file', follower_urdf,
                    '-x', '-3', '-y', '0', '-z', '0.2',
                ],
                output='screen',
            )
        ],
    )

    # 4. Bridge: leader cmd_vel (ROS → Gazebo)
    bridge_leader_cmd = TimerAction(
        period=7.0,
        actions=[
            Node(
                package='ros_gz_bridge',
                executable='parameter_bridge',
                arguments=[
                    '/leader/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
                ],
                output='screen',
            )
        ],
    )

    # 5. Bridge: follower cmd_vel (ROS → Gazebo)
    bridge_follower_cmd = TimerAction(
        period=7.0,
        actions=[
            Node(
                package='ros_gz_bridge',
                executable='parameter_bridge',
                arguments=[
                    '/follower/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
                ],
                output='screen',
            )
        ],
    )

    # 6. Bridge: Gazebo odometry → ROS (leader)
    bridge_leader_odom = TimerAction(
        period=7.0,
        actions=[
            Node(
                package='ros_gz_bridge',
                executable='parameter_bridge',
                arguments=[
                    '/model/leader_car/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry',
                ],
                output='screen',
            )
        ],
    )

    # 7. Bridge: Gazebo odometry → ROS (follower)
    bridge_follower_odom = TimerAction(
        period=7.0,
        actions=[
            Node(
                package='ros_gz_bridge',
                executable='parameter_bridge',
                arguments=[
                    '/model/follower_car/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry',
                ],
                output='screen',
            )
        ],
    )

    # 8. Leader node (drives in circle)
    leader_node = TimerAction(
        period=8.0,
        actions=[
            Node(
                package='gazebo_follower',
                executable='leader_node',
                output='screen',
            )
        ],
    )

    # 9. Follower node (follows leader using odometry)
    follower_node = TimerAction(
        period=9.0,
        actions=[
            Node(
                package='gazebo_follower',
                executable='follower_node',
                output='screen',
            )
        ],
    )

    return LaunchDescription([
        gz_sim,
        spawn_leader,
        spawn_follower,
        bridge_leader_cmd,
        bridge_follower_cmd,
        bridge_leader_odom,
        bridge_follower_odom,
        leader_node,
        follower_node,
    ])
