import argparse
import os

from mininet_ros.emulate_network import emulate_ros_network
from mininet_ros.host_options import HostOptions


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'ros_setup_bash',
        nargs='?',
        default='/opt/ros/rolling/setup.bash',
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
    # Available Topic names at the time of writing:
    #   - Array1k
    #   - Array4k
    #   - Array16k
    #   - Array32k
    #   - Array60k
    #   - Array1m
    #   - Array2m
    #   - Struct16
    #   - Struct256
    #   - Struct4k
    #   - Struct32k
    #   - PointCloud512k
    #   - PointCloud1m
    #   - PointCloud2m
    #   - PointCloud4m
    #   - Range
    #   - NavSatFix
    #   - RadarDetection
    #   - RadarTrack
    parser.add_argument(
        '--topic-name',
        default='Array1k',
        type=str,
        help='Topic name to use with the tests, indicates the message type used',
    )
    parser.add_argument(
        '--rate',
        default=0,
        type=int,
        help=(
            'The rate data should be published. Defaults to 1000 Hz.'
            '0 means publish as fast as possible.'),
    )
    parser.add_argument(
        '--reliability',
        choices=['reliable', 'best_effort'],
        default='reliable',
        type=str,
        help='The reliability QoS setting for both the publisher and subscriber.',
    )
    parser.add_argument(
        '--durability',
        choices=['volatile', 'transient_local'],
        default='volatile',
        type=str,
        help='The durability QoS setting for both the publisher and subscriber.',
    )
    parser.add_argument(
        '--history-kind',
        choices=['keep_last', 'keep_all'],
        default='keep_last',
        type=str,
        help='The history kind QoS setting for both the publisher and subscriber.',
    )
    parser.add_argument(
        '--history-depth',
        default=1000,
        type=int,
        help='The history depth QoS setting for both the publisher and subscriber.',
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
    )
    parser.add_argument(
        '--disable-async',
        default=False,
        action='store_true',
        help='If using rmw_fastrtps_cpp, disable asynchornous publishing'
    )

    args = parser.parse_args()

    common_cmd = [
        'ros2',
        'run',
        'performance_test',
        'perf_test',
        '-c',
        'ROS2',
        '-t',
        f'{args.topic_name}',
        '-r',
        f'{args.rate}',
        '--max_runtime',
        f'{args.duration}',
    ]
    if args.reliability == 'reliable':
        common_cmd.append('--reliable')
    if args.durability == 'transient_local':
        common_cmd.append('--transient')
    if args.history_kind == 'keep_last':
        common_cmd.append('--keep_last')
    common_cmd.append('--history_depth')
    common_cmd.append(f'{args.history_depth}')
    if args.disable_async and args.rmw_implementation == 'rmw_fastrtps_cpp':
        xml = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'DEFAULT_FASTRTPS_PROFILES_TWO_PROCESSES.xml')
        common_cmd = \
            ['export', 'RMW_FASTRTPS_USE_QOS_FROM_XML=1', '&&'] + \
            ['export', f'FASTRTPS_DEFAULT_PROFILES_FILE={xml}', '&&'] + \
            common_cmd

    host_options = [
        HostOptions(
            command=common_cmd + [
                '-l',
                'pub_log',
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
            command=common_cmd + [
                '-l',
                'sub_log',
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
