import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    IncludeLaunchDescription,
    LogInfo,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():

    pkg_dir = get_package_share_directory("delivery_robot")
    launches = os.path.join(pkg_dir, "launch")

    # ----- Arguments -----
    mode = LaunchConfiguration("mode", default="slam")  # Mode switch
    use_sim_time = LaunchConfiguration("use_sim_time", default="true")
    map_yaml = LaunchConfiguration("map", default=os.path.join(pkg_dir, "maps", "delivery_map.yaml"))

    # Declare arguments
    declare_mode = DeclareLaunchArgument("mode", default_value="slam")
    declare_sim = DeclareLaunchArgument("use_sim_time", default_value="true")
    declare_map = DeclareLaunchArgument("map", default_value=map_yaml)

    # Conditions
    is_slam = PythonExpression(["'", mode, "' == 'slam'"])
    is_nav = PythonExpression(["'", mode, "' == 'navigation'"])

    # ----- Gazebo (always runs) -----
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(launches, "gazebo.launch.py")),
        launch_arguments={"use_sim_time": use_sim_time}.items(),
    )

    # ----- SLAM mode -----
    slam = GroupAction(
        condition=IfCondition(is_slam),
        actions=[
            LogInfo(msg="SLAM MODE"),
            TimerAction(
                period=3.0,  # Wait for Gazebo
                actions=[
                    IncludeLaunchDescription(
                        PythonLaunchDescriptionSource(os.path.join(launches, "slam.launch.py")),
                        launch_arguments={"use_sim_time": use_sim_time}.items(),
                    )
                ],
            ),
        ],
    )

    # ----- Navigation mode -----
    navigation = GroupAction(
        condition=IfCondition(is_nav),
        actions=[
            LogInfo(msg="NAVIGATION MODE"),
            TimerAction(
                period=3.0,
                actions=[
                    IncludeLaunchDescription(
                        PythonLaunchDescriptionSource(os.path.join(launches, "navigation.launch.py")),
                        launch_arguments={"use_sim_time": use_sim_time, "map": map_yaml}.items(),
                    )
                ],
            ),
            TimerAction(
                period=8.0,  # Wait for Nav2
                actions=[
                    Node(
                        package="delivery_robot",
                        executable="waypoint_navigator.py",  # Moves robot
                    ),
                    Node(
                        package="delivery_robot",
                        executable="delivery_manager.py",   # Manages tasks
                    ),
                ],
            ),
        ],
    )

    # ----- RViz -----
    rviz = TimerAction(
        period=5.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(os.path.join(launches, "rviz.launch.py")),
                launch_arguments={"use_sim_time": use_sim_time}.items(),
            )
        ],
    )

    return LaunchDescription([
        declare_mode,
        declare_sim,
        declare_map,
        gazebo,       # Always run
        slam,         # Conditional
        navigation,   # Conditional
        rviz,         # Visualization
    ])
