from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Start Turtlesim
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='sim'
        ),
        # Start Spawner
        Node(
            package='turtle_spawner',
            executable='turtle_spawner',
            name='spawner'
        ),
        # Start Broadcaster for Turtle 1
        Node(
            package='turtle_tf_broadcaster',
            executable='turtle_tf_broadcaster',
            name='broadcaster1',
            parameters=[{'turtlename': 'turtle1'}]
        ),
        # Start Broadcaster for Turtle 2
        Node(
            package='turtle_tf_broadcaster',
            executable='turtle_tf_broadcaster',
            name='broadcaster2',
            parameters=[{'turtlename': 'turtle2'}]
        ),
    ])