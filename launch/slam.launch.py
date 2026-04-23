import os  # For file paths

from ament_index_python.packages import get_package_share_directory  # Get package path
from launch import LaunchDescription  # Main container
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node  # To launch ROS nodes


def generate_launch_description():

    pkg_dir = get_package_share_directory("delivery_robot")  # Your project folder
    pkg_slam = get_package_share_directory("slam_toolbox")   # SLAM toolbox folder

    # Use simulation time (important for Gazebo)
    use_sim_time = LaunchConfiguration("use_sim_time", default="true")

    # Path to YAML config file
    slam_params = LaunchConfiguration(
        "slam_params_file",
        default=os.path.join(pkg_dir, "config", "slam_toolbox_params.yaml"),
    )

    # Allow user to override simulation time
    declare_sim = DeclareLaunchArgument(
        "use_sim_time", default_value="true",
        description="Use simulation clock",
    )

    # Allow user to override config file
    declare_params = DeclareLaunchArgument(
        "slam_params_file",
        default_value=os.path.join(pkg_dir, "config", "slam_toolbox_params.yaml"),
    )

    # Include SLAM Toolbox's built-in launch file
    slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_slam, "launch", "online_async_launch.py")
        ),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "slam_params_file": slam_params,
        }.items(),
    )

    return LaunchDescription([
        declare_sim,     # Declare arguments
        declare_params,
        slam_toolbox,    # Start SLAM
    ])
