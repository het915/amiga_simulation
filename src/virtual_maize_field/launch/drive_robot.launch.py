"""Launch corn field simulation with Amiga robot and teleop control.

Usage:
    ros2 launch virtual_maize_field drive_robot.launch.py

Then in another terminal:
    ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/cmd_vel
"""
from __future__ import annotations

import math
import os
import re
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    LogInfo,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _read_spawn_pose(cache_dir: str) -> dict:
    """Read robot spawn position from the generated robot_spawner.launch.py."""
    spawner_file = os.path.join(cache_dir, "robot_spawner.launch.py")
    defaults = {"x": 0.0, "y": 0.0, "z": 0.5, "yaw": 0.0}
    if not os.path.isfile(spawner_file):
        return defaults
    content = Path(spawner_file).read_text()
    for key in ["x", "y", "z", "Y"]:
        match = re.search(rf'"-{key}",\s*"([^"]+)"', content)
        if match:
            val = float(match.group(1))
            if key == "Y":
                defaults["yaw"] = val
            else:
                defaults[key] = val
    defaults["z"] = 0.5  # always drop from above to settle on suspension
    return defaults


def generate_launch_description() -> LaunchDescription:
    pkg_share = Path(get_package_share_directory("virtual_maize_field"))
    ros_home = os.environ.get("ROS_HOME", os.path.join(os.path.expanduser("~"), ".ros"))
    cache_dir = os.path.join(ros_home, "virtual_maize_field/")
    model_sdf = str(pkg_share / "models" / "amiga" / "model.sdf")
    urdf_path = pkg_share / "models" / "amiga" / "amiga.urdf"
    urdf_content = urdf_path.read_text()

    # Read spawn pose from generated world
    pose = _read_spawn_pose(cache_dir)
    # Convert yaw to quaternion (rotation around Z)
    qz = math.sin(pose["yaw"] / 2)
    qw = math.cos(pose["yaw"] / 2)

    headless = LaunchConfiguration("headless")
    declare_headless = DeclareLaunchArgument(
        "headless", default_value="False", description="Run without GUI"
    )

    # 1. Launch the corn field simulation
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            str(pkg_share / "launch" / "simulation.launch.py")
        ),
        launch_arguments={"headless": headless}.items(),
    )

    # 2. Spawn the Amiga robot (delayed to let sim start)
    spawn_robot = TimerAction(
        period=8.0,
        actions=[
            LogInfo(msg="Spawning Amiga robot..."),
            ExecuteProcess(
                cmd=[
                    "ign", "service",
                    "-s", "/world/virtual_maize_field/create",
                    "--reqtype", "ignition.msgs.EntityFactory",
                    "--reptype", "ignition.msgs.Boolean",
                    "--timeout", "10000",
                    "--req",
                    f"sdf_filename: '{model_sdf}', name: 'amiga', "
                    f"pose: {{position: {{x: {pose['x']:.4f}, y: {pose['y']:.4f}, z: {pose['z']:.4f}}}, "
                    f"orientation: {{x: 0, y: 0, z: {qz:.6f}, w: {qw:.6f}}}}}",
                ],
                output="screen",
            ),
        ],
    )

    # 3. Bridge cmd_vel from ROS2 to Ignition
    cmd_vel_bridge = TimerAction(
        period=12.0,
        actions=[
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                name="cmd_vel_bridge",
                arguments=["/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist"],
                output="screen",
            ),
        ],
    )

    # 4. Bridge odometry from Ignition to ROS2
    odom_bridge = TimerAction(
        period=12.0,
        actions=[
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                name="odom_bridge",
                arguments=["/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry"],
                output="screen",
            ),
        ],
    )

    # 5. Bridge joint states from Ignition to ROS2
    joint_states_bridge = TimerAction(
        period=12.0,
        actions=[
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                name="joint_states_bridge",
                arguments=[
                    "/world/virtual_maize_field/model/amiga/joint_state@sensor_msgs/msg/JointState[ignition.msgs.Model",
                ],
                remappings=[
                    ("/world/virtual_maize_field/model/amiga/joint_state", "/joint_states"),
                ],
                output="screen",
            ),
        ],
    )

    # 6. Bridge camera RGB image
    rgb_bridge = TimerAction(
        period=12.0,
        actions=[
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                name="rgb_bridge",
                arguments=[
                    "/world/virtual_maize_field/model/amiga/link/oak_link/sensor/oak_d_camera/image@sensor_msgs/msg/Image[ignition.msgs.Image",
                ],
                remappings=[
                    ("/world/virtual_maize_field/model/amiga/link/oak_link/sensor/oak_d_camera/image", "/oak/rgb"),
                ],
                output="screen",
            ),
        ],
    )

    # 7. Bridge camera depth image
    depth_bridge = TimerAction(
        period=12.0,
        actions=[
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                name="depth_bridge",
                arguments=[
                    "/world/virtual_maize_field/model/amiga/link/oak_link/sensor/oak_d_camera/depth_image@sensor_msgs/msg/Image[ignition.msgs.Image",
                ],
                remappings=[
                    ("/world/virtual_maize_field/model/amiga/link/oak_link/sensor/oak_d_camera/depth_image", "/oak/depth"),
                ],
                output="screen",
            ),
        ],
    )

    # 8. Bridge camera info
    cam_info_bridge = TimerAction(
        period=12.0,
        actions=[
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                name="cam_info_bridge",
                arguments=[
                    "/world/virtual_maize_field/model/amiga/link/oak_link/sensor/oak_d_camera/camera_info@sensor_msgs/msg/CameraInfo[ignition.msgs.CameraInfo",
                ],
                remappings=[
                    ("/world/virtual_maize_field/model/amiga/link/oak_link/sensor/oak_d_camera/camera_info", "/oak/camera_info"),
                ],
                output="screen",
            ),
        ],
    )

    # 9. Bridge point cloud
    points_bridge = TimerAction(
        period=12.0,
        actions=[
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                name="points_bridge",
                arguments=[
                    "/world/virtual_maize_field/model/amiga/link/oak_link/sensor/oak_d_camera/points@sensor_msgs/msg/PointCloud2[ignition.msgs.PointCloudPacked",
                ],
                remappings=[
                    ("/world/virtual_maize_field/model/amiga/link/oak_link/sensor/oak_d_camera/points", "/oak/points"),
                ],
                output="screen",
            ),
        ],
    )

    # 10. Robot state publisher (for TF)
    robot_state_publisher = TimerAction(
        period=12.0,
        actions=[
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                parameters=[{"robot_description": urdf_content}],
            ),
        ],
    )

    return LaunchDescription([
        declare_headless,
        sim_launch,
        spawn_robot,
        cmd_vel_bridge,
        odom_bridge,
        joint_states_bridge,
        rgb_bridge,
        depth_bridge,
        cam_info_bridge,
        points_bridge,
        robot_state_publisher,
    ])
