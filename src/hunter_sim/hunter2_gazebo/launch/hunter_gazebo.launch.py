import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, AppendEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Paths and Definitions
    urdf_filename = 'hunter2_base_gazebo.xacro'
    
    hunter_base_pkg_share = get_package_share_directory('hunter2_base')
    hunter_gazebo_pkg_share = get_package_share_directory('hunter2_gazebo')

    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    
    urdf_file = os.path.join(hunter_base_pkg_share, 'urdf', urdf_filename)
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    workspace_share = os.path.dirname(hunter_base_pkg_share)

    # 2. Add the share directory to Gazebo's resource path
    set_resource_path = AppendEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=workspace_share
    )

    # 2. Start Gazebo
    gz_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f"-r {os.path.join(hunter_gazebo_pkg_share, 'world', 'mars_dome.world')}"}.items(),
    )

    # 3. Start the Robot State Publisher
    # This broadcasts the URDF to the ROS network on the /robot_description topic
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': True # Crucial: tells ROS to use Gazebo's clock
        }]
    )

    # 4. Spawn the Entity into Gazebo
    # The 'create' executable grabs the structure from /robot_description
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'hunter2',
            '-z', '0.5' # Spawn slightly above ground to prevent clipping
        ],
        output='screen'
    )
    
    # 5. Start the ROS-Gazebo Bridge
    # Example: Bridging the /cmd_vel topic (Twist) from ROS to Gazebo
    # and /odom (Odometry) from Gazebo to ROS
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # Topic@ROS_Type[Direction]Gazebo_Type
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry'
        ],
        output='screen'
    )

    return LaunchDescription([
        set_resource_path,
        gz_server,
        robot_state_publisher,
        spawn_robot,
        bridge
    ])