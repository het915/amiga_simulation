"""Launch file to visualize the Amiga robot in RViz2.

Usage:
    ros2 launch virtual_maize_field view_robot.launch.py
"""
from __future__ import annotations

from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    pkg_share = Path(get_package_share_directory("virtual_maize_field"))
    urdf_path = pkg_share / "models" / "amiga" / "amiga.urdf"
    urdf_content = urdf_path.read_text()
    rviz_config = str(pkg_share / "rviz" / "amiga.rviz")

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": urdf_content}],
    )

    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
    )

    rviz2 = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", rviz_config],
    )

    return LaunchDescription([
        robot_state_publisher,
        joint_state_publisher,
        rviz2,
    ])
