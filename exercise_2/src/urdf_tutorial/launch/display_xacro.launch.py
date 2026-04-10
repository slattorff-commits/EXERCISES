from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    xacro_file = get_package_share_directory('urdf_tutorial') + '/urdf/simple_box.xacro'
    doc = xacro.process_file(xacro_file)
    robot_description_config = doc.toxml()

    return LaunchDescription(
        [
            Node(
                package='robot_state_publisher',
                executable='robot_state_publisher',
                parameters=[{'robot_description': robot_description_config}],
            ),
            Node(
                package='joint_state_publisher_gui',
                executable='joint_state_publisher_gui',
            ),
            Node(
                package='tf2_ros',
                executable='static_transform_publisher',
                arguments=['0', '0', '0', '0', '0', '0', 'map', 'base_link'],
            ),
            Node(
                package='rviz2',
                executable='rviz2',
                name='rviz2',
            ),
        ]
    )