import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_path = get_package_share_directory('iha_gazebo')
    world_file = os.path.join(pkg_path, 'worlds', 'competition.sdf')
    ros_gz_sim_pkg = get_package_share_directory('ros_gz_sim')
    models_path = os.path.join(pkg_path, 'models')
    worlds_path = os.path.join(pkg_path, 'worlds')
    resource_path = models_path + ':' + worlds_path
    return LaunchDescription([
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', resource_path),
        SetEnvironmentVariable('IGN_GAZEBO_RESOURCE_PATH', resource_path),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(ros_gz_sim_pkg, 'launch', 'gz_sim.launch.py')
            ),
            launch_arguments={'gz_args': world_file}.items(),
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/iha/imu@sensor_msgs/msg/Imu@gz.msgs.IMU',
                '/iha/gps@sensor_msgs/msg/NavSatFix@gz.msgs.NavSat',
                '/iha_camera/image_raw@sensor_msgs/msg/Image@gz.msgs.Image',
                '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
                '/model/iha/odometry@nav_msgs/msg/Odometry@gz.msgs.Odometry',
                '/world/competition/pose/info@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
                '/model/iha/servo_0@std_msgs/msg/Float64@gz.msgs.Double',
                '/model/iha/servo_1@std_msgs/msg/Float64@gz.msgs.Double',
                '/model/iha/servo_2@std_msgs/msg/Float64@gz.msgs.Double',
                '/model/iha/servo_3@std_msgs/msg/Float64@gz.msgs.Double',
                '/model/iha/command/motor_speed@actuator_msgs/msg/Actuators@gz.msgs.Actuators',
                '/model/iha/rotor_velocity@std_msgs/msg/Float64@gz.msgs.Double',
            ],
            parameters=[{'lazy': False}],
            output='screen'
        ),
    ])