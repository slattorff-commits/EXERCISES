#!/usr/bin/env python3
"""
Follower node: subscribes to leader and follower odometry from Gazebo,
computes the relative position, and steers the follower toward the leader.
"""
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


class FollowerNode(Node):
    def __init__(self):
        super().__init__('follower_node')

        self.pub = self.create_publisher(Twist, '/follower/cmd_vel', 10)

        self.create_subscription(
            Odometry, '/model/leader_car/odometry', self.leader_odom_cb, 10
        )
        self.create_subscription(
            Odometry, '/model/follower_car/odometry', self.follower_odom_cb, 10
        )

        self.leader_x = None
        self.leader_y = None
        self.follower_x = None
        self.follower_y = None
        self.follower_yaw = None

        self.timer = self.create_timer(0.1, self.on_timer)
        self.get_logger().info('Follower node started – waiting for odometry')

    def leader_odom_cb(self, msg: Odometry):
        self.leader_x = msg.pose.pose.position.x
        self.leader_y = msg.pose.pose.position.y

    def follower_odom_cb(self, msg: Odometry):
        self.follower_x = msg.pose.pose.position.x
        self.follower_y = msg.pose.pose.position.y
        qz = msg.pose.pose.orientation.z
        qw = msg.pose.pose.orientation.w
        self.follower_yaw = 2.0 * math.atan2(qz, qw)

    def on_timer(self):
        if (
            self.leader_x is None
            or self.follower_x is None
            or self.follower_yaw is None
        ):
            return

        dx = self.leader_x - self.follower_x
        dy = self.leader_y - self.follower_y
        dist = math.sqrt(dx * dx + dy * dy)
        angle_to_leader = math.atan2(dy, dx)

        # Angle error relative to follower heading
        angle_err = angle_to_leader - self.follower_yaw
        angle_err = math.atan2(math.sin(angle_err), math.cos(angle_err))

        cmd = Twist()
        if dist > 0.5:
            cmd.linear.x = min(0.6, 0.5 * dist)
            cmd.angular.z = 2.0 * angle_err
        else:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.5 * angle_err

        self.pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = FollowerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
