#!/usr/bin/env python3
import math

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

from action_msg.action import ReachEdgeAndReturn
from rclpy.executors import MultiThreadedExecutor
import time

CENTER_X = 5.5
CENTER_Y = 5.5
EDGE_THRESHOLD = 0.2
CENTER_THRESHOLD = 0.3


class ReachEdgeActionServer(Node):
    def __init__(self):
        super().__init__('reach_edge_action_server')

        self.pose = None

        self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        self.server = ActionServer(
            self,
            ReachEdgeAndReturn,
            'reach_edge_and_return',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
        )

        self.get_logger().info('ReachEdgeAndReturn Action Server ready.')

    def pose_callback(self, msg: Pose):
        self.pose = msg

    def goal_callback(self, goal_request):
        self.get_logger().info('Goal received.')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Cancel requested.')
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        feedback = ReachEdgeAndReturn.Feedback()
        result = ReachEdgeAndReturn.Result()

        # PHASE 1: GO TO EDGE
        self.get_logger().info('Phase 1: Moving to edge...')
        while not self.is_at_edge():
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.stop()
                result.success = False
                return result

            self.move_forward(speed=2.0)

            feedback.phase = 'going_to_edge'
            feedback.distance = self.distance_to_edge()
            goal_handle.publish_feedback(feedback)
            time.sleep(0.1)

        self.stop()
        self.get_logger().info('Reached edge!')

        # PHASE 2: RETURN TO CENTER
        self.get_logger().info('Phase 2: Returning to center...')
        while not self.is_at_center():
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.stop()
                result.success = False
                return result

            self.move_towards_center(speed=2.0, k_ang=4.0)

            feedback.phase = 'returning_to_center'
            feedback.distance = self.distance_to_center()
            goal_handle.publish_feedback(feedback)
            time.sleep(0.1)

        self.stop()
        self.get_logger().info('Reached center!')

        goal_handle.succeed()
        result.success = True
        return result

    def stop(self):
        twist = Twist()
        self.cmd_pub.publish(twist)

    def move_forward(self, speed=2.0):
        twist = Twist()
        twist.linear.x = speed
        self.cmd_pub.publish(twist)

    def move_towards_center(self, speed=2.0, k_ang=4.0):
        if self.pose is None:
            return

        dx = CENTER_X - self.pose.x
        dy = CENTER_Y - self.pose.y
        target_theta = math.atan2(dy, dx)

        err = target_theta - self.pose.theta
        err = math.atan2(math.sin(err), math.cos(err))

        twist = Twist()
        twist.linear.x = speed
        twist.angular.z = k_ang * err
        self.cmd_pub.publish(twist)

    def is_at_edge(self) -> bool:
        if self.pose is None:
            return False

        x = self.pose.x
        y = self.pose.y

        return (
            x < EDGE_THRESHOLD or x > (11.0 - EDGE_THRESHOLD) or
            y < EDGE_THRESHOLD or y > (11.0 - EDGE_THRESHOLD)
        )

    def is_at_center(self) -> bool:
        if self.pose is None:
            return False

        dx = CENTER_X - self.pose.x
        dy = CENTER_Y - self.pose.y
        dist = math.sqrt(dx*dx + dy*dy)
        return dist < CENTER_THRESHOLD

    def distance_to_edge(self) -> float:
        if self.pose is None:
            return float('inf')

        x = self.pose.x
        y = self.pose.y

        d_left = x
        d_right = 11.0 - x
        d_bottom = y
        d_top = 11.0 - y

        return min(d_left, d_right, d_bottom, d_top)

    def distance_to_center(self) -> float:
        if self.pose is None:
            return float('inf')
        return math.sqrt((CENTER_X - self.pose.x)**2 + (CENTER_Y - self.pose.y)**2)

def main():
    rclpy.init()
    node = ReachEdgeActionServer()

    executor = MultiThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()