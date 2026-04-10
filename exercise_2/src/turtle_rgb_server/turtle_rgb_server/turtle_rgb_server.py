#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from turtle_rgb.srv import SetRGB


class TurtleRGBServer(Node):
    def __init__(self):
        super().__init__('turtle_rgb_server')
        self.service = self.create_service(SetRGB, '/set_rgb', self.set_rgb_callback)
        self.get_logger().info('Service /set_rgb ready.')

    def set_rgb_callback(self, request, response):
        self.get_logger().info(
            f'Received RGB request: r={request.r}, g={request.g}, b={request.b}'
        )
        response.success = True
        return response


def main(args=None):
    rclpy.init(args=args)
    node = TurtleRGBServer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()