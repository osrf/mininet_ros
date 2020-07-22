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
        default=15,
        type=int,
        help='max duration in seconds',
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
        '--bandwidth',
        default=None,
        type=int,
        help='Bandwidth limit per node in Mbps',
    )
    parser.add_argument(
        '--loss',
        default=0,
        type=int,
        help='Percentage packet loss per node (0-100)',
    )
    parser.add_argument(
        '--delay',
        default=0,
        type=int,
        help='Latency per node in milliseconds',
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
    )

    args = parser.parse_args()

    host_options = [
        HostOptions(
            command=[
                'ros2',
                'run',
                'performance_test',
                'perf_test',
                '-c',
                'ROS2',
                '-l',
                'pub_log',
                '-t',
                'Array1k',
                '--max_runtime',
                f'{args.duration}',
                '--num_sub_threads',
                '0',
                '--num_pub_threads',
                '1',
            ],
            ros_setup_bash=args.ros_setup_bash,
            ros_domain_id=args.ros_domain_id,
            rmw_implementation=args.rmw_implementation,
        ),
        HostOptions(
            command=[
                'ros2',
                'run',
                'performance_test',
                'perf_test',
                '-c',
                'ROS2',
                '-l',
                'sub_log',
                '-t',
                'Array1k',
                '--max_runtime',
                f'{args.duration}',
                '--num_sub_threads',
                '1',
                '--num_pub_threads',
                '0',
            ],
            ros_setup_bash=args.ros_setup_bash,
            ros_domain_id=args.ros_domain_id,
            rmw_implementation=args.rmw_implementation,
        ),
    ]

    emulate_ros_network(
        host_options=host_options,
        bandwidth=args.bandwidth,
        loss=args.loss,
        delay=args.delay,
        verbose=args.verbose,
    )
