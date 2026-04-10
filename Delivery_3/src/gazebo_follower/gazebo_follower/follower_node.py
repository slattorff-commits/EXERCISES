#!/usr/bin/env python3
"""
Follower node: subscribes to world-frame poses from Gazebo via the
dynamic_pose/info bridge and steers the follower toward the leader.
"""
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from tf2_msgs.msg import TFMessage


class FollowerNode(Node):
    def __init__(self):
        super().__init__('follower_node')

        self.pub = self.create_publisher(Twist, '/follower/cmd_vel', 10)

        # dynamic_pose/info bridged as TFMessage: index 0 = leader, 1 = follower
        self.create_subscription(
            TFMessage,
            '/world/empty_class3/dynamic_pose/info',
            self.pose_cb,
            10,
        )

        self.leader_x = None
        self.leader_y = None
        self.follower_x = None
        self.follower_y = None
        self.follower_yaw = None

        self.timer = self.create_timer(0.1, self.on_timer)
        self.get_logger().info('Follower node started – waiting for world poses')

    def pose_cb(self, msg: TFMessage):
        if len(msg.transforms) < 2:
            return
        # Index 0 = leader_car (spawned first, entity id 10)
        leader_tf = msg.transforms[0]
        self.leader_x = leader_tf.transform.translation.x
        self.leader_y = leader_tf.transform.translation.y

        # Index 1 = follower_car (spawned second, entity id 30)
        follower_tf = msg.transforms[1]
        self.follower_x = follower_tf.transform.translation.x
        self.follower_y = follower_tf.transform.translation.y
        qz = follower_tf.transform.rotation.z
        qw = follower_tf.transform.rotation.w
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
