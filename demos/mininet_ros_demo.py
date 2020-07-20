import argparse

from mininet_ros.emulate_network import emulate_ros_network


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'ros_setup_bash',
        nargs='?',
        default='/opt/ros/foxy/setup.bash',
        help='path to a setup.bash file for a ROS installation',
    )
    parser.add_argument(
        '-d', '--duration',
        default=5.0,
        type=float,
        help='how long to run talker and listener nodes',
    )
    parser.add_argument(
        '--ros-domain-id',
        default=42,
        type=int,
        help='ROS domain ID',
    )
    args = parser.parse_args()

    emulate_ros_network(
        ros_setup_bash=args.ros_setup_bash,
        host_1_cmd=['ros2', 'run', 'demo_nodes_cpp', 'talker'],
        host_2_cmd=['ros2', 'run', 'demo_nodes_cpp', 'listener'],
        duration=args.duration,
        ros_domain_id=args.ros_domain_id,
    )
