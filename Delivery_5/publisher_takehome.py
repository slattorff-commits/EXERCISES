"""
Exercise 4 Take-home — MQTT Publisher (multiple topics)
========================================================
Publishes both /odom position and /scan minimum range over MQTT.

Run:
  python3 publisher_takehome.py
"""

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

BROKER = 'broker.hivemq.com'
PORT   = 1883

TOPIC_ODOM = 'robotics_class/slattorff/odom'
TOPIC_SCAN = 'robotics_class/slattorff/scan'


class MqttPublisher(Node):

    def __init__(self):
        super().__init__('mqtt_publisher')

        # MQTT client
        self.mqtt = mqtt.Client(CallbackAPIVersion.VERSION2)
        self.mqtt.connect(BROKER, PORT)
        self.mqtt.loop_start()

        # ROS 2 subscriptions
        self.create_subscription(Odometry, '/odom', self._odom_cb, 10)
        self.create_subscription(LaserScan, '/laser/scan', self._scan_cb, 10)

        self.get_logger().info(f'Publishing to {BROKER}')

    def _odom_cb(self, msg: Odometry):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        value = f'x={x:.2f} y={y:.2f}'
        self.mqtt.publish(TOPIC_ODOM, value)
        self.get_logger().info(f'[MQTT] {TOPIC_ODOM}: {value}')

    def _scan_cb(self, msg: LaserScan):
        valid = [r for r in msg.ranges if msg.range_min <= r <= msg.range_max]
        min_range = min(valid) if valid else float('inf')
        value = f'min_range={min_range:.2f}'
        self.mqtt.publish(TOPIC_SCAN, value)
        self.get_logger().info(f'[MQTT] {TOPIC_SCAN}: {value}')


def main():
    rclpy.init()
    node = MqttPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
