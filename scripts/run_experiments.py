import datetime
import json
import os
import signal
import shutil
import subprocess
import sys


def find_root_of_docker(path=os.getcwd()):
    if os.path.exists(os.path.join(path, 'Dockerfile')):
        return path
    if path.lstrip(os.sep) == '':
        raise RuntimeError('Failed to find the root of the Dockerfile')
    return find_root_of_docker(os.path.dirname(path))


def do_it(*, rmw_implementation, bandwidth, loss, delay, rate, topic_type, async_pub, repeat=1):
    reliability = 'reliable'
    durability = 'volatile'
    history_kind = 'keep_last'
    history_depth = 10
    history = 'keep_all' if history_kind == 'keep_all' else f'keep_last@{history_depth}'

    rmw_impl_str = f'{rmw_implementation}_{async_pub}'

    orig_dir = os.getcwd()
    dir_name = f'{rmw_impl_str}_{topic_type}@{rate}_{reliability}_{durability}_{history}_{bandwidth}bw_{loss}loss_{delay}delay'
    os.makedirs(dir_name)
    os.chdir(dir_name)

    assert repeat > 0
    run = 1
    while True:
        experiment_dir = os.getcwd()
        run_dir = f'run{run:02}'
        os.makedirs(run_dir)
        os.chdir(run_dir)

        root_of_docker = find_root_of_docker()

        experiment_config = {
            'rmw_implementation': rmw_implementation,
            'async_pub': async_pub,
            'bandwidth': bandwidth,
            'loss': loss,
            'delay': delay,
            'message_rate': rate,
            'message_type': topic_type,
            'reliability': reliability,
            'durability': durability,
            'history_kind': history_kind,
            'history_depth': history_depth,
        }
        with open('experiment_config.json', 'w+') as f:
            f.write(json.dumps(experiment_config, indent=4))

        print(json.dumps(experiment_config, indent=4))

        common_args = [
            '--rmw-implementation', f'{rmw_implementation}',
            '--bandwidth', f'{bandwidth}',
            '--loss', f'{loss}',
            '--delay', f'{delay}',
            '--topic-name', f'{topic_type}',
            '--rate', f'{rate}',
            '--reliability', reliability,
            '--durability', durability,
            '--history-kind', history_kind,
            '--history-depth', str(history_depth),
        ]
        if async_pub == 'sync':
            common_args.append('--disable-async')
        cmd = [
            sys.executable,
            os.path.join(root_of_docker, 'demos/mininet_ros_perf_demo.py'),
        ] + common_args
        print('Running cmd: ' + ' '.join(cmd))
        assert os.path.exists(cmd[1])
        should_retry = False
        try:
            try:
                p = subprocess.Popen(cmd)
                p.wait(timeout=30)
            except subprocess.TimeoutExpired:
                print('Timeout occurred, will retry')
                should_retry = True
                p.send_signal(signal.SIGINT)
                p.wait()
        except KeyboardInterrupt:
            pass

        if p.returncode != 0:
            print('mininet_ros_perf_demo.py failed unexpectedly, will retry')
            should_retry = True

        if should_retry:
            os.chdir(experiment_dir)
            shutil.rmtree(run_dir)
            continue

        cmd = [
            sys.executable,
            os.path.join(root_of_docker, 'demos/plot_perf.py'),
        ] + common_args
        print('Running cmd: ' + ' '.join(cmd))
        assert os.path.exists(cmd[1])
        cp = subprocess.run(' '.join(cmd), shell=True)
        if cp.returncode == 42:
            print('plotting failed due to insufficient data, will retry')
            should_retry = True
        elif cp.returncode != 0:
            sys.exit('plotting failed unexpectedly')

        if should_retry:
            os.chdir(experiment_dir)
            shutil.rmtree(run_dir)
            continue

        os.chdir(experiment_dir)

        run += 1
        if run > repeat:
            break

    os.chdir(orig_dir)


if __name__ == '__main__':
    rmw_implementations = [
        ('rmw_fastrtps_cpp', 'async'),
        ('rmw_fastrtps_cpp', 'sync'),
        ('rmw_cyclonedds_cpp', 'sync'),
    ]
    # bandwidths = [
    #     11,  # 802.11a/b
    #     54,  # 802.11g
    #     72,  # 802.11n low
    #     433,  # 802.11ac low
    #     600,  # 802.11n high
    #     1000,  # 1000BASE-T
    #     1300,  # 802.11n mid
    #     6933,  # 802.11n high
    # ]
    # losses = range(0, 100, 10)
    # delays = range(0, 1000, 100)
    bandwidths = [
        # 7,  # 802.11a/b poor
        # 11,  # 802.11a/b
        54,  # 802.11g
        300,  # 802.11n
        1000,  # 1000BASE-T
    ]
    losses = [0, 10, 20, 30, 40]
    delays = [0]

    rates = [30]
    types = [
        'Array1k',
        # 'Array1m',
        'PointCloud512k',
        # 'PointCloud2m',
    ]

    dir_name = os.path.join(os.getcwd(), datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    os.makedirs(dir_name)
    os.chdir(dir_name)

    for (rmw_implementation, async_pub) in rmw_implementations:
        for bandwidth in bandwidths:
            for loss in losses:
                for delay in delays:
                    for rate in rates:
                        for topic_type in types:
                            do_it(
                                rmw_implementation=rmw_implementation,
                                bandwidth=bandwidth,
                                loss=loss,
                                delay=delay,
                                topic_type=topic_type,
                                rate=rate,
                                async_pub=async_pub,
                                repeat=10,
                            )

    print('Done!')
