from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    nav_efrei_dir = get_package_share_directory('ros2_nav_efrei')
    nav2_launch_file_dir = os.path.join(get_package_share_directory('nav2_bringup'), 'launch')
    rviz_config_dir = os.path.join(
        get_package_share_directory('ros2_nav_efrei'),
        'rviz',
        'nav_view.rviz')
    
    param_dir = LaunchConfiguration(
        'params_file',
        default=os.path.join(
            get_package_share_directory('ros2_nav_efrei'),
            'params',
            'slam_param.yaml'))
    map_dir = LaunchConfiguration(
        'map',
        default=os.path.join(
            get_package_share_directory('ros2_nav_efrei'),
            'map',
            'cave_world.yaml'))

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    resolution = LaunchConfiguration('resolution', default='0.05')
    publish_period_sec = LaunchConfiguration('publish_period_sec', default='1.0')

    cartographer_config_dir = LaunchConfiguration('cartographer_config_dir', default=os.path.join(
                                                  nav_efrei_dir, 'config'))
    configuration_basename = LaunchConfiguration('configuration_basename',
                                                 default='robot_lds_2d.lua')

    ld = LaunchDescription()

    # simulated world
    stage_launch = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    FindPackageShare("stage_ros2"), '/launch', '/stage.launch.py']))
      
    ld.add_action(stage_launch)
    
    # cartographer node
    carto_node =   Node(
            package='cartographer_ros',
            executable='cartographer_node',
            name='cartographer_node',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}],
            remappings=[('/scan', '/base_scan')],
            arguments=['-configuration_directory', cartographer_config_dir,
                       '-configuration_basename', configuration_basename])
    ld.add_action(carto_node)

    # rviz node
    rviz_node = Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_dir],
            parameters=[{'use_sim_time': use_sim_time}],
            output='screen')
    ld.add_action(rviz_node)

    # navigation 2
    nav2_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([nav2_launch_file_dir, '/bringup_launch.py']),
            launch_arguments={
                'map': map_dir,
                'use_sim_time': use_sim_time,
                'params_file': param_dir}.items(),
        )
    ld.add_action(nav2_launch)


    # ocupancy grid node
    ocupancy_node = Node(
            package='cartographer_ros',
            executable='cartographer_occupancy_grid_node',
            name='cartographer_occupancy_grid_node',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}],
            arguments=['-resolution', resolution, 
                       '-publish_period_sec', publish_period_sec])
    ld.add_action(ocupancy_node)

    # explorer 
    explorer_node = Node(
        package='final_project',
        executable='action_server_client',
        name='exploration_node',
        output='screen'
    )
    ld.add_action(explorer_node)

    # launch arguments
    resolution_arg = DeclareLaunchArgument(
            'resolution',
            default_value=resolution,
            description='Resolution of a grid cell in the published occupancy grid')
    ld.add_action(resolution_arg)

    publish_period_arg = DeclareLaunchArgument(
            'publish_period_sec',
            default_value=publish_period_sec,
            description='OccupancyGrid publishing period')
    ld.add_action(publish_period_arg)

    use_sim_time_arg = DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation (Gazebo) clock if true')
    ld.add_action(use_sim_time_arg)

    return ld
