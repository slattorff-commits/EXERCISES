#!/usr/bin/env python3
"""Leader node: drives the leader car in a circle pattern in Gazebo."""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class LeaderNode(Node):
    def __init__(self):
        super().__init__('leader_node')
        self.pub = self.create_publisher(Twist, '/leader/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.on_timer)
        self.get_logger().info('Leader node started – driving in circles')

    def on_timer(self):
        msg = Twist()
        msg.linear.x = 0.5
        msg.angular.z = 0.3
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = LeaderNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
