# Copyright (C) 2026 Jasmeet Singh
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import xacro


def generate_launch_description():
	this_package = get_package_share_directory('gz_led_plugin')
	example_dir = os.path.join(this_package, 'examples', 'ros')
	urdf_file = os.path.join(example_dir, 'urdf', 'led_robot.urdf.xacro')

	# Robot description xacro file
	urdf_doc = xacro.process_file(urdf_file)
	robot_description_str = urdf_doc.toprettyxml(indent='  ')

	# Launch Gazebo with empty world only if use_sim_time is true
	gazebo_launch = IncludeLaunchDescription(
		PythonLaunchDescriptionSource([
			os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
		]),
		launch_arguments=[('gz_args', '-r -v 4 empty.sdf')]
	)

	# Robot State Publisher
	robot_state_publisher_node = Node(
		package='robot_state_publisher',
		executable='robot_state_publisher',
		output='screen',
		parameters=[
			{'use_sim_time': True},
			{'robot_description': robot_description_str}
		]
	)

	# Spawn robot in Gazebo
	spawn_robot = Node(
		package='ros_gz_sim',
		executable='create',
		arguments=[
			'-topic', 'robot_description',
			'-name', 'led_robot',
			'-z', '0.335'
		],
		output='screen'
	)

	# Bridge the LED mode change topic from ROS 2 to Gazebo
	led_mode_bridge = Node(
		package='ros_gz_bridge',
		executable='parameter_bridge',
		arguments=[
			'/led_robot/change_led_mode@std_msgs/msg/String]gz.msgs.StringMsg'
		],
		output='screen'
	)

	return LaunchDescription([
		gazebo_launch,
		robot_state_publisher_node,
		spawn_robot,
		led_mode_bridge,
	])
