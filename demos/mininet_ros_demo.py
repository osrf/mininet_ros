import argparse

from mininet_ros.emulate_network import emulate_ros_network
from mininet_ros.host_options import HostOptions


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
    parser.add_argument(
        '--rmw-implementation',
        default=None,
        type=str,
        help='RWM implementation identifier',
    )
    parser.add_argument(
        '--localhost-only',
        action='store_true',
        help='Use localhost only',
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output',
    )
    args = parser.parse_args()

    host_options = [
        HostOptions(
            command=['ros2', 'run', 'demo_nodes_cpp', 'talker'],
            ros_setup_bash=args.ros_setup_bash,
            ros_domain_id=args.ros_domain_id,
            rmw_implementation=args.rmw_implementation,
            localhost_only=args.localhost_only,
        ),
        HostOptions(
            command=['ros2', 'run', 'demo_nodes_cpp', 'listener'],
            ros_setup_bash=args.ros_setup_bash,
            ros_domain_id=args.ros_domain_id,
            rmw_implementation=args.rmw_implementation,
            localhost_only=args.localhost_only,
        ),
    ]

    emulate_ros_network(
        host_options=host_options,
        duration=args.duration,
        verbose=args.verbose
    )
