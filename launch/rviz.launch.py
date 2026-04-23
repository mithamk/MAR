import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    pkg_dir = get_package_share_directory("delivery_robot")  # Get project path

    use_sim_time = LaunchConfiguration("use_sim_time", default="true")

    # Path to RViz config file
    rviz_config = LaunchConfiguration(
        "rviz_config",
        default=os.path.join(pkg_dir, "rviz", "delivery_robot.rviz"),
    )

    # Declare arguments
    declare_sim = DeclareLaunchArgument("use_sim_time", default_value="true")
    declare_rviz = DeclareLaunchArgument("rviz_config", default_value=rviz_config)

    # Launch RViz
    rviz = Node(
        package="rviz2",        # RViz package
        executable="rviz2",     # RViz executable
        name="rviz2",
        arguments=["-d", rviz_config],  # Load saved config
        parameters=[{"use_sim_time": use_sim_time}],  # Sync time
        output="screen",
    )

    return LaunchDescription([
        declare_sim,
        declare_rviz,
        rviz,   # Start visualization
    ])
