#!/usr/bin/env python3
"""
Finite State Machine robot node for Exercise 7 (Session 4).

States:
  EXPLORE — Rotate slowly to search for the red target.
  TRACK   — Move toward the red object using camera centroid.
  AVOID   — Turn away from a LiDAR obstacle.
  STOP    — Halt when IMU detects angular-velocity spike or tilt.

Subscriptions:
  /laser/scan        (sensor_msgs/LaserScan)
  /camera/image_raw  (sensor_msgs/Image)
  /imu               (sensor_msgs/Imu)

Publication:
  /cmd_vel           (geometry_msgs/Twist)
"""

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan, Image, Imu
from cv_bridge import CvBridge
import cv2
import numpy as np


# ── thresholds ──────────────────────────────────────────────
OBSTACLE_DIST = 0.6          # metres – triggers AVOID
CLEAR_DIST = 1.0             # metres – exits AVOID
RED_AREA_MIN = 500           # pixels – minimum blob area to count as "detected"
IMU_GYRO_THRESH = 3.0        # rad/s – angular-velocity spike → STOP
IMU_TILT_THRESH = 0.5        # rad   – roll/pitch from quaternion → STOP
IMAGE_WIDTH = 640             # expected camera width in pixels


class FSMRobot(Node):
    def __init__(self):
        super().__init__('fsm_robot')

        # publisher
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # subscribers
        self.create_subscription(LaserScan, '/laser/scan', self.laser_cb, 10)
        self.create_subscription(Image, '/camera/image_raw', self.image_cb, 10)
        self.create_subscription(Imu, '/imu', self.imu_cb, 10)

        # cv_bridge
        self.bridge = CvBridge()

        # sensor state
        self.min_laser = float('inf')
        self.red_detected = False
        self.red_cx = IMAGE_WIDTH // 2      # centroid x
        self.red_area = 0
        self.imu_spike = False

        # FSM
        self.state = 'EXPLORE'
        self.get_logger().info('FSM started in EXPLORE')

        # control timer – 10 Hz
        self.create_timer(0.1, self.control_loop)

    # ── sensor callbacks ────────────────────────────────────
    def laser_cb(self, msg: LaserScan):
        valid = [r for r in msg.ranges if msg.range_min <= r <= msg.range_max]
        self.min_laser = min(valid) if valid else float('inf')

    def image_cb(self, msg: Image):
        cv_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)

        # red in HSV wraps around 0/180
        mask1 = cv2.inRange(hsv, np.array([0, 120, 70]), np.array([10, 255, 255]))
        mask2 = cv2.inRange(hsv, np.array([170, 120, 70]), np.array([180, 255, 255]))
        mask = cv2.bitwise_or(mask1, mask2)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest)
            if area > RED_AREA_MIN:
                x, y, w, h = cv2.boundingRect(largest)
                self.red_cx = x + w // 2
                self.red_area = area
                self.red_detected = True
                return
        self.red_detected = False
        self.red_area = 0

    def imu_cb(self, msg: Imu):
        gx = msg.angular_velocity.x
        gy = msg.angular_velocity.y
        gz = msg.angular_velocity.z
        gyro_mag = math.sqrt(gx * gx + gy * gy + gz * gz)

        # extract roll/pitch from quaternion
        q = msg.orientation
        sinr = 2.0 * (q.w * q.x + q.y * q.z)
        cosr = 1.0 - 2.0 * (q.x * q.x + q.y * q.y)
        roll = math.atan2(sinr, cosr)

        sinp = 2.0 * (q.w * q.y - q.z * q.x)
        sinp = max(-1.0, min(1.0, sinp))
        pitch = math.asin(sinp)

        self.imu_spike = (
            gyro_mag > IMU_GYRO_THRESH
            or abs(roll) > IMU_TILT_THRESH
            or abs(pitch) > IMU_TILT_THRESH
        )

    # ── FSM control loop ────────────────────────────────────
    def control_loop(self):
        cmd = Twist()
        prev_state = self.state

        # ── global transition: any → STOP ───────────────────
        if self.imu_spike:
            self.state = 'STOP'

        # ── state logic ─────────────────────────────────────
        if self.state == 'STOP':
            # halt
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
            # recover when IMU is normal again
            if not self.imu_spike:
                self.state = 'EXPLORE'

        elif self.state == 'AVOID':
            # turn away from obstacle
            cmd.linear.x = 0.0
            cmd.angular.z = 0.5          # rotate in place
            if self.min_laser > CLEAR_DIST:
                self.state = 'EXPLORE'

        elif self.state == 'EXPLORE':
            if self.min_laser < OBSTACLE_DIST:
                self.state = 'AVOID'
            elif self.red_detected:
                self.state = 'TRACK'
            else:
                # rotate slowly to search
                cmd.linear.x = 0.0
                cmd.angular.z = 0.3

        elif self.state == 'TRACK':
            if self.min_laser < OBSTACLE_DIST:
                self.state = 'AVOID'
            elif not self.red_detected:
                self.state = 'EXPLORE'
            else:
                # proportional steering toward red centroid
                error = (self.red_cx - IMAGE_WIDTH / 2) / (IMAGE_WIDTH / 2)
                cmd.linear.x = 0.3
                cmd.angular.z = -1.0 * error

        # re-evaluate new state for cmd if we just transitioned
        if self.state != prev_state:
            self.get_logger().info(f'State: {prev_state} → {self.state}')

        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = FSMRobot()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        stop = Twist()
        node.cmd_pub.publish(stop)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
