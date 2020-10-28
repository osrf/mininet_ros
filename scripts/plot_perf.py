import argparse
from glob import glob
import sys

from buildfarm_perf_tests.test_results import read_performance_test_csv

import matplotlib  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np  # noqa: F401
import pandas as pd

plt.switch_backend('agg')


def generate_plots(dataframe, mode, args):
    pd.options.display.float_format = '{:.4f}'.format

    rmw_impl = args.rmw_implementation
    bandwidth = args.bandwidth
    loss = args.loss
    delay = args.delay
    topic_name = args.topic_name
    rate = args.rate
    reliability = args.reliability
    durability = args.durability
    history_kind = args.history_kind
    history_depth = args.history_depth

    pd.options.display.float_format = '{:.4f}'.format
    if len(dataframe['sent']) != 15:
        print('Not enough data taken, failing with returncode 42...')
        sys.exit(42)  # signal that not enough data was taken
    dataframe.plot(kind='bar', y=['received', 'sent', 'lost'])
    async_str = 'sync'
    if rmw_impl == 'rmw_fastrtps_cpp':
        async_str = 'sync' if args.disable_async else 'async'
    rmw_impl_str = f'{rmw_impl} {async_str}'
    title_details = mode + ': ' + rmw_impl_str + \
        ', ' + reliability + ', ' + durability + ', ' + \
        ('keep_all' if history_kind == 'keep_all' else 'keep_last ' + str(history_depth)) + \
        ',\nbandwidth: ' + ('No limit' if bandwidth is None else str(bandwidth) + ' Mbps') + \
        ', packet loss: ' + str(loss) + '%' + \
        ', delay: ' + str(delay) + ' ms'
    plt.title(
        f'{topic_name}@{rate}Hz Pub/Sub Received/Sent/Lost messages\n' + title_details)
    plt.savefig(mode + '_histogram.png')

    dataframe['maxrss (Mb)'] = dataframe['ru_maxrss'] / 1e3
    dataframe.drop(list(dataframe.filter(regex='ru_')), axis=1, inplace=True)
    dataframe['latency_variance (ms) * 100'] = 100.0 * dataframe['latency_variance (ms)']
    dataframe[[
        'T_experiment',
        'latency_min (ms)',
        'latency_max (ms)',
        'latency_mean (ms)',
        'latency_variance (ms) * 100',
        'maxrss (Mb)'
    ]].plot(x='T_experiment', secondary_y=['maxrss (Mb)'])
    plt.title(f'{topic_name}@{rate}Hz Pub/Sub latency\n' + title_details)
    plt.savefig(mode + '_latency.png')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
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
        '--disable-async',
        default=False,
        action='store_true',
        help='If using rmw_fastrtps_cpp, disable asynchornous publishing'
    )

    args = parser.parse_args()
    assert args.rmw_implementation is not None, 'argument --rmw-implementation must be provided'

    performance_logs = glob('pub_log_*')
    assert len(performance_logs) == 1
    performance_data = read_performance_test_csv(performance_logs[0])

    generate_plots(performance_data, 'publisher', args)

    performance_logs = glob('sub_log_*')
    assert len(performance_logs) == 1
    performance_data = read_performance_test_csv(performance_logs[0])

    generate_plots(performance_data, 'subscriber', args)
