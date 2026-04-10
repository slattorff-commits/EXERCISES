import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
import math

class TurtleFollower(Node):
    def __init__(self):
        super().__init__('turtle_follower')

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.publisher = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.on_timer)

    def on_timer(self):
        try:
            # Lookup the transform: where is 'turtle1' relative to 'turtle2'
            trans = self.tf_buffer.lookup_transform(
                'turtle2',
                'turtle1',
                rclpy.time.Time())

        except TransformException as ex:
            self.get_logger().info(f'Could not transform: {ex}')
            return

        msg = Twist()

        # Extract relative distances from the transform
        dx = trans.transform.translation.x
        dy = trans.transform.translation.y

        # Proportional controller
        msg.angular.z = 1.0 * math.atan2(dy, dx)
        msg.linear.x = 0.5 * math.sqrt(dx**2 + dy**2)

        self.publisher.publish(msg)

def main():
    rclpy.init()
    node = TurtleFollower()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()