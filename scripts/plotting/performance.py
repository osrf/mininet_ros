import json
import os

from datetime import datetime
from glob import glob

import pandas
import matplotlib.pyplot as plt
import numpy


def generate_averaged_sent_received_plot(df, output_dir, *, ax=None):
    if ax is None:
        fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.set_xlabel('Time in Seconds')
    ax.set_ylabel('Number of Messages')
    ax.grid(which='both')

    pub_datasets = []
    sub_datasets = []

    for index, row in df.iterrows():
        ax.plot(row['pub_log'].sent, color='blue', alpha=0.2)
        pub_datasets.append(row['pub_log'].sent)
        ax.plot(row['sub_log'].received, color='orange', alpha=0.2)
        ax.axhline(y=row['sub_log'].received.mean(), color='orange', linestyle='--', alpha=0.2)
        sub_datasets.append(row['sub_log'].received)

    number_of_runs = len(df)

    pubs_mean = pandas.DataFrame(pub_datasets).mean(axis=0)
    pubs_mean_mean = pubs_mean.mean()
    ax.plot(
        pubs_mean, color='blue',
        label=f'Average Messages Sent N={number_of_runs} ({pubs_mean_mean:1.1f})')
    ax.axhline(y=pubs_mean_mean, color='blue', linestyle='--')

    subs_mean = pandas.DataFrame(sub_datasets).mean(axis=0)
    subs_mean_mean = subs_mean.mean()
    ax.plot(
        subs_mean, color='orange',
        label=f'Average Messages Received N={number_of_runs} ({subs_mean_mean:1.1f})')
    ax.axhline(y=subs_mean_mean, color='orange', linestyle='--')

    ax.legend()

    e = df.iloc[0]
    if output_dir is not None:
        title = \
            f"{e['message_type']}@{e['message_rate']}Hz 1 Pub to 1 Sub, multi-processes, single machine\n" + \
            f"{e['rmw_implementation']} {e['async_pub']}, {e['reliability']}, {e['durability']}, " + \
            ('keep_all' if e['history_kind'] == 'keep_all' else f"keep_last@{e['history_depth']}") + '\n' + \
            f"bandwidth: {e['bandwidth']}Mbps, packet loss: {e['loss']}%, delay: {e['delay']}ms"
        ax.set_title(title)

    ax.set_ylim((0, int(1.1 * int(e['message_rate']))))
    ax.set_xlim((1, len(e['pub_log'].sent) + 1))

    if output_dir is not None:
        local_output_dir = os.path.join(output_dir, os.path.basename(e['directory']))
        if not os.path.exists(local_output_dir):
            os.makedirs(local_output_dir)
        plot_output_prefix = os.path.join(local_output_dir, 'average_sent_received')
        ax.get_figure().savefig(plot_output_prefix + '.svg', bbox_inches='tight')
        ax.get_figure().savefig(plot_output_prefix + '.png', bbox_inches='tight')

        plt.close()

        return plot_output_prefix


def generate_averaged_latency_plot(df, output_dir, *, ax=None):
    if ax is None:
        fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.set_xlabel('Time in Seconds')
    ax.set_ylabel('Latency in Milliseconds')
    ax.grid(which='both')

    latency_means = []
    latency_variances = []

    for index, row in df.iterrows():
        latency_mean_with_inf = [
            (numpy.inf if numpy.isinf(lmax) else lmean)
            for (lmean, lmax) in row['sub_log'][['latency_mean (ms)', 'latency_max (ms)']].values
        ]
        ax.plot(latency_mean_with_inf, color='red', alpha=0.2)
        latency_means.append(latency_mean_with_inf)
        latency_variance_with_inf = [
            (numpy.inf if numpy.isinf(lmax) else lvar)
            for (lvar, lmax) in row['sub_log'][['latency_variance (ms)', 'latency_max (ms)']].values
        ]
        ax.plot(latency_variance_with_inf, color='purple', alpha=0.2)
        latency_variances.append(latency_variance_with_inf)

    number_of_runs = len(df)

    latency_means_mean = pandas.DataFrame(latency_means).mean(axis=0)
    latency_means_mean_mean = latency_means_mean.mean()
    ax.plot(
        latency_means_mean, color='red',
        label=f'Average Latency Mean N={number_of_runs} ({latency_means_mean_mean:1.1f})')
    ax.axhline(y=latency_means_mean_mean, color='red', linestyle='--')

    latency_variances_mean = pandas.DataFrame(latency_variances).mean(axis=0)
    latency_variances_mean_mean = latency_variances_mean.mean()
    ax.plot(
        latency_variances_mean, color='purple',
        label=f'Average Latency Variance N={number_of_runs} ({latency_variances_mean_mean:1.1f})')
    ax.axhline(y=latency_variances_mean_mean, color='purple', linestyle='--')

    ax.legend()

    e = df.iloc[0]
    if output_dir is not None:
        title = \
            f"{e['message_type']}@{e['message_rate']}Hz 1 Pub to 1 Sub, multi-processes, single machine\n" + \
            f"{e['rmw_implementation']} {e['async_pub']}, {e['reliability']}, {e['durability']}, " + \
            ('keep_all' if e['history_kind'] == 'keep_all' else f"keep_last@{e['history_depth']}") + '\n' + \
            f"bandwidth: {e['bandwidth']}Mbps, packet loss: {e['loss']}%, delay: {e['delay']}ms"
        ax.set_title(title)

    ax.set_xlim((1, len(e['sub_log']['latency_mean (ms)']) + 1))

    if output_dir is not None:
        local_output_dir = os.path.join(output_dir, os.path.basename(e['directory']))
        if not os.path.exists(local_output_dir):
            os.makedirs(local_output_dir)
        plot_output_prefix = os.path.join(local_output_dir, 'average_latency')
        ax.get_figure().savefig(plot_output_prefix + '.svg', bbox_inches='tight')
        ax.get_figure().savefig(plot_output_prefix + '.png', bbox_inches='tight')

        plt.close()

        return plot_output_prefix


def generate_averaged_resource_plot(df, output_dir, *, ax=None):
    if ax is None:
        fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.set_xlabel('Time in Seconds')
    ax.set_ylabel('Publisher CPU Utilization Percentage')
    ax.grid(which='both')
    ax2 = ax.twinx()
    ax2.set_ylabel('Publisher Memory Usage in Kilobytes')
    ax2.grid(which='both')

    cpu_datasets = []
    maxrss_datasets = []

    for index, row in df.iterrows():
        # ax.plot(row['pub_log']['cpu_usage (%)'], color='green', alpha=0.2)
        cpu_datasets.append(row['pub_log']['cpu_usage (%)'])
        ax.axhline(y=row['pub_log']['cpu_usage (%)'].mean(), color='green', linestyle='--', alpha=0.2)

        ax2.plot(row['pub_log']['ru_maxrss'], color='magenta', alpha=0.2)
        ax2.axhline(y=row['pub_log']['ru_maxrss'].mean(), color='magenta', linestyle='--', alpha=0.2)
        maxrss_datasets.append(row['pub_log']['ru_maxrss'])

    number_of_runs = len(df)

    cpu_mean = pandas.DataFrame(cpu_datasets).mean(axis=0)
    cpu_mean_mean = cpu_mean.mean()
    cpu_line = ax.plot(
        cpu_mean, color='green',
        label=f'Average CPU Utilization N={number_of_runs} ({cpu_mean_mean:1.1f} %)')
    ax.axhline(y=cpu_mean_mean, color='green', linestyle='--')

    maxrss_mean = pandas.DataFrame(maxrss_datasets).mean(axis=0)
    maxrss_mean_mean = maxrss_mean.mean()
    maxrss_line = ax2.plot(
        maxrss_mean, color='magenta',
        label=f'Average Memory Usage (ru_maxrss) N={number_of_runs} ({maxrss_mean_mean:1.1f} kb)')
    ax2.axhline(y=maxrss_mean_mean, color='magenta', linestyle='--')

    lines = cpu_line + maxrss_line
    ax.legend(lines, [line.get_label() for line in lines])

    e = df.iloc[0]
    if output_dir is not None:
        title = \
            f"{e['message_type']}@{e['message_rate']}Hz 1 Pub to 1 Sub, multi-processes, single machine\n" + \
            f"{e['rmw_implementation']} {e['async_pub']}, {e['reliability']}, {e['durability']}, " + \
            ('keep_all' if e['history_kind'] == 'keep_all' else f"keep_last@{e['history_depth']}") + '\n' + \
            f"bandwidth: {e['bandwidth']}Mbps, packet loss: {e['loss']}%, delay: {e['delay']}ms"
        ax.set_title(title)

    ax.set_xlim((1, len(e['pub_log']['latency_mean (ms)']) + 1))

    if output_dir is not None:
        local_output_dir = os.path.join(output_dir, os.path.basename(e['directory']))
        if not os.path.exists(local_output_dir):
            os.makedirs(local_output_dir)
        plot_output_prefix = os.path.join(local_output_dir, 'resource')
        ax.get_figure().savefig(plot_output_prefix + '.svg', bbox_inches='tight')
        ax.get_figure().savefig(plot_output_prefix + '.png', bbox_inches='tight')

        plt.close()

        return plot_output_prefix


def read_performance_test_csv(csv_path, start_marker='---EXPERIMENT-START---\n'):
    """
    Taken from from buildfarm_perf_tests.test_results import read_performance_test_csv.
    """
    with open(csv_path, 'r') as csv:
        if start_marker:
            while csv.readline() not in [start_marker, '']:
                pass
        return pandas.read_csv(csv, sep='[ \t]*,[ \t]*', engine='python')


def find_all_experiments(directory):
    """
    Find all experiments marked by a `experiment_config.json`.
    """
    experiment_configs = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == 'experiment_config.json':
                experiment_configs.append(os.path.join(root, file))
    return experiment_configs


def parse_run_dir(run_dir):
    run_dir_split = run_dir.split('run')
    assert len(run_dir_split) == 2 and run_dir_split[0] == '', \
        f"expected run dir of style 'run01', got '{run_dir}'"
    return int(run_dir_split[1])


def parse_experiment_config_dir(experiment_config_dir):
    for key_token in ['_', '@', 'delay', 'loss', 'bw']:
        assert key_token in experiment_config_dir, \
            f"expected '{key_token}' in '{experiment_config_dir}'"


def parse_experiment_group_dir(experiment_group_dir):
    (date, time) = experiment_group_dir.split('_')
    (year, month, day) = date.split('-')
    (hour, minute, second) = time.split('-')
    return datetime(
        int(year),
        int(month),
        int(day),
        int(hour),
        int(minute),
        int(second),
    )


def get_pub_log_from_run_dir(run_dir):
    pub_logs = glob(os.path.join(run_dir, 'pub_log_*'))
    assert len(pub_logs) == 1, f"expected exactly one pub log, found '{pub_logs}' in '{run_dir}'"
    df = read_performance_test_csv(pub_logs[0])
    df.index = range(1, len(df.sent) + 1)
    return df


def get_sub_log_from_run_dir(run_dir):
    sub_logs = glob(os.path.join(run_dir, 'sub_log_*'))
    assert len(sub_logs) == 1, f"expected exactly one sub log, found '{sub_logs}' in '{run_dir}'"
    df = read_performance_test_csv(sub_logs[0])
    df.index = range(1, len(df.sent) + 1)
    return df


def collect_experiments(directory):
    """
    Find all experiments and return them as a pandas DataFrame.

    Expected structure is:

    */*
    │   # A group of experiments created with `experiments/run_experiments.py`.
    ├── YYYY-MM-DD_HH-MM-SS
    │   │   # A single experiment configuration, run multiple times.
    │   ├── <rmw_impl>_<message_type>@<message_rate>_<reliability>_<durability>_<history>@<depth>_<bandwidth>bw_<packet_loss>loss_<delay>delay
    │   │   │   # A single experiment, with configuration and performance data.
    │   │   ├── run01
    │   │   │   ├── experiment_config.json
    │   │   │   ├── pub_log_<message_type>_DD-MM-YYYY_HH-MM-SS
    │   │   │   ├── sub_log_<message_type>_DD-MM-YYYY_HH-MM-SS


    The resulting data structure will look like this:

    # One entry for each group of experiments from `experiements/run_experiments.py`
    {
        <Datetime based on the folder name>: pandas.DataFrame({
            # One entry for each experiment configuration.
            'directory': <directory of experiment configuration>,
            'run': <run number>,
            'pub_log': pandas.DataFrame({
                # Fields based on output from `perf_test` node in `performance_test` package.
                # See `buildfarm_perf_tests.test_results.read_performance_test_csv()`.
                T_experiment: [...],
                T_loop: [...],
                received: [...],
                sent: [...],
                lost: [...],
                relative_loss: [...],
                data_received: [...],
                latency_min (ms): [...],
                latency_max (ms): [...],
                latency_mean (ms): [...],
                latency_variance (ms): [...],
                pub_loop_res_min (ms): [...],
                pub_loop_res_max (ms): [...],
                pub_loop_res_mean (ms): [...],
                pub_loop_res_variance (ms): [...],
                sub_loop_res_min (ms): [...],
                sub_loop_res_max (ms): [...],
                sub_loop_res_mean (ms): [...],
                sub_loop_res_variance (ms): [...],
                ru_utime: [...],
                ru_stime: [...],
                ru_maxrss: [...],
                ru_ixrss: [...],
                ru_idrss: [...],
                ru_isrss: [...],
                ru_minflt: [...],
                ru_majflt: [...],
                ru_nswap: [...],
                ru_inblock: [...],
                ru_oublock: [...],
                ru_msgsnd: [...],
                ru_msgrcv: [...],
                ru_nsignals: [...],
                ru_nvcsw: [...],
                ru_nivcsw: [...],
                cpu_usage (%): [...],
            }),
            'sub_log': <same as pub_log>,
            'rmw_implementation': ...,
            'bandwidth': ...,
            'loss': ...,
            'delay': ...,
            'message_rate': ...,
            'message_type': ...,
            'reliability': ...,
            'durability': ...,
            'history_kind': ...,
            'history_depth': ...,
        }),
    }
    """
    # Find all the experiments.
    experiment_configs = find_all_experiments(directory)

    # Build initial dict for dataframe
    result = {}
    for experiment_config in experiment_configs:
        dirname = os.path.dirname(experiment_config)

        run_dir_full = str(dirname)
        (dirname, run_dir) = os.path.split(dirname)
        run = parse_run_dir(run_dir)

        parse_experiment_config_dir(os.path.basename(dirname))
        experiment_config_dir = str(dirname)
        dirname = os.path.dirname(dirname)

        (dirname, experiment_group_dir) = os.path.split(dirname)
        experiment_group_datetime = parse_experiment_group_dir(experiment_group_dir)

        if experiment_group_datetime not in result:
            result[experiment_group_datetime] = {
                'directory': [],
                'run': [],
                'pub_log': [],
                'sub_log': [],
                'rmw_implementation': [],
                'async_pub': [],
                'bandwidth': [],
                'loss': [],
                'delay': [],
                'message_rate': [],
                'message_type': [],
                'reliability': [],
                'durability': [],
                'history_kind': [],
                'history_depth': [],
            }

        result[experiment_group_datetime]['directory'].append(experiment_config_dir)
        result[experiment_group_datetime]['run'].append(run)
        result[experiment_group_datetime]['pub_log'].append(get_pub_log_from_run_dir(run_dir_full))
        result[experiment_group_datetime]['sub_log'].append(get_sub_log_from_run_dir(run_dir_full))

        with open(experiment_config) as fp:
            experiment_config_dict = json.load(fp)

        for key, value in experiment_config_dict.items():
            result[experiment_group_datetime][key].append(value)

    # Build experiment dataframes
    for k, v in result.items():
        result[k] = pandas.DataFrame(v)

    return result
