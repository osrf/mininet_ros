import argparse
import os

import markdown

from plotting.performance import collect_experiments
from plotting.performance import generate_averaged_latency_plot
from plotting.performance import generate_averaged_resource_plot
from plotting.performance import generate_averaged_sent_received_plot


def generate_loss_plot_pair(df, output_dir, plot_output_prefix):
    e = df.iloc[0]  # get first experiment for loss percent
    relative_plot_output_prefix = os.path.relpath(plot_output_prefix, os.getcwd())
    return (e['loss'], relative_plot_output_prefix)


def generate_averaged_plot_html_table_pair(loss_plot_pair):
    header_template = '    <td>Packet Loss: {}%</td>'
    image_template = '    <td valign="top"><img src="{}"></td>'
    return (header_template.format(loss_plot_pair[0]), image_template.format(loss_plot_pair[1] + '.svg'))


def get_one_item(df, key):
    results = set(df[key])
    assert len(results) == 1, key
    return list(results)[0]


def generate_html_table_for_single_config(df, html_table_pairs_by_directory):
    rmw_implementation = get_one_item(df, 'rmw_implementation')
    async_pub = get_one_item(df, 'async_pub')
    headers = []
    sent_received_images = []
    latency_images = []
    resource_images = []
    # Use this set to avoid visiting duplicates, using a set on the sorted values would unsort them.
    visited_directories = set()
    for directory in df.sort_values('loss')['directory']:
        if directory in visited_directories:
            continue
        visited_directories.add(directory)
        h, sent_received_i = html_table_pairs_by_directory[directory]['sent_received']
        latency_h, latency_i = html_table_pairs_by_directory[directory]['latency']
        assert h == latency_h
        resource_h, resource_i = html_table_pairs_by_directory[directory]['resource']
        assert h == resource_h
        headers.append(h)
        sent_received_images.append(sent_received_i)
        latency_images.append(latency_i)
        resource_images.append(resource_i)
    headers = '\n'.join(headers)
    sent_received_images = '\n'.join(sent_received_images)
    latency_images = '\n'.join(latency_images)
    resource_images = '\n'.join(resource_images)

    snippet = f"""\
#### {rmw_implementation} {async_pub}

<table>
  <tr>
{headers}
  </tr>
  <tr>
{sent_received_images}
  </tr>
  <tr>
{latency_images}
  </tr>
  <tr>
{resource_images}
  </tr>
</table>

"""
    return snippet


def generate_markdown_table_for_single_config(df, loss_plot_pairs_by_directory):
    rmw_implementation = get_one_item(df, 'rmw_implementation')
    async_pub = get_one_item(df, 'async_pub')
    md = f"""\
#### {rmw_implementation} {async_pub}

"""
    # Use this set to avoid visiting duplicates, using a set on the sorted values would unsort them.
    visited_directories = set()
    for directory in df.sort_values('loss')['directory']:
        if directory in visited_directories:
            continue
        visited_directories.add(directory)
        loss, sent_received_img = loss_plot_pairs_by_directory[directory]['sent_received']
        latency_loss, latency_img = loss_plot_pairs_by_directory[directory]['latency']
        assert loss == latency_loss
        resource_loss, resource_img = loss_plot_pairs_by_directory[directory]['resource']
        assert loss == resource_loss
        md += f"""\
##### Packet Loss: {loss}%

![]({sent_received_img + '.png'})

![]({latency_img + '.png'})

![]({resource_img + '.png'})

"""
    return md
#     rmw_implementation = get_one_item(df, 'rmw_implementation')
#     md = f"""\
# #### {rmw_implementation}

# """
#     # Use this set to avoid visiting duplicates, using a set on the sorted values would unsort them.
#     visited_directories = set()
#     pairs = []
#     for directory in df.sort_values('loss')['directory']:
#         if directory in visited_directories:
#             continue
#         visited_directories.add(directory)
#         pairs.append(loss_plot_pairs_by_directory[directory])
#     header = ""
#     divider = ""
#     row = ""
#     for i, (loss, img) in enumerate(pairs):
#         header += f"Packet Loss: {loss}%"
#         if i != len(pairs) - 1:
#             header += " | "
#         divider += '---'
#         if i != len(pairs) - 1:
#             divider += " | "
#         row += f"![]({img + '.png'})"
#         if i != len(pairs) - 1:
#             row += " | "
#     md += f"""\
# {header}
# {divider}
# {row}

# """
#     return md


def markdown_for_list_of_things(things):
    md = ""
    for i, thing in enumerate(things):
        md += str(thing)
        if len(things) == 2 and i != len(things) - 1:
            md += " and "
        elif len(things) > 2:
            if i == len(things) - 2:
                md += ", and "
            elif i != len(things) - 1:
                md += ", "
    return md


def markdown_for_rmw_implementations(df):
    a = df[['rmw_implementation', 'async_pub']]
    rmw_implementations = set([(x['rmw_implementation'], x['async_pub']) for i, x in a.iterrows()])
    rmw_implementations = [f'{rmw} {async_pub}' for rmw, async_pub in rmw_implementations]
    return markdown_for_list_of_things(rmw_implementations)


def markdown_for_bandwidths(df):
    bandwidths = set(df['bandwidth'])
    return markdown_for_list_of_things(bandwidths)


def markdown_for_message_type_rate_combos(df):
    message_type_rate_combos = set(map(tuple, df[['message_type', 'message_rate']].values))
    message_type_rate_combos = [f'{t}@{r}' for t, r in message_type_rate_combos]
    return markdown_for_list_of_things(message_type_rate_combos)


def generate_report(log_dir, output_dir):
    # First collect all experiment data.
    experiment_groups = collect_experiments(log_dir)

    assert len(experiment_groups.keys()) == 1, "expected just one group"
    first_group_date = list(experiment_groups.keys())[0]
    experiements_df = experiment_groups[first_group_date]

    # Generate plots for each set of runs, showing averaged sent/received plots.
    directories_set = set()
    for index, row in experiements_df.iterrows():
        directories_set.add(row['directory'])
    loss_plot_pairs_by_directory = {}
    html_table_pairs_by_directory = {}
    for directory in directories_set:
        print(f'=== Generating plot for experiment in directory: {directory}')
        directory_experiments_df = experiements_df[experiements_df.directory == directory]
        sent_received_plot_output_prefix = generate_averaged_sent_received_plot(directory_experiments_df, output_dir)
        sent_received_loss_plot_pair = generate_loss_plot_pair(
            directory_experiments_df,
            output_dir,
            sent_received_plot_output_prefix)
        latency_plot_output_prefix = generate_averaged_latency_plot(directory_experiments_df, output_dir)
        latency_loss_plot_pair = generate_loss_plot_pair(
            directory_experiments_df,
            output_dir,
            latency_plot_output_prefix)
        resource_plot_output_prefix = generate_averaged_resource_plot(directory_experiments_df, output_dir)
        resource_loss_plot_pair = generate_loss_plot_pair(
            directory_experiments_df,
            output_dir,
            resource_plot_output_prefix)
        loss_plot_pairs_by_directory[directory] = {
            'sent_received': sent_received_loss_plot_pair,
            'latency': latency_loss_plot_pair,
            'resource': resource_loss_plot_pair,
        }
        sent_received_html_table_pair = generate_averaged_plot_html_table_pair(sent_received_loss_plot_pair)
        latency_html_table_pair = generate_averaged_plot_html_table_pair(latency_loss_plot_pair)
        resource_html_table_pair = generate_averaged_plot_html_table_pair(resource_loss_plot_pair)
        html_table_pairs_by_directory[directory] = {
            'sent_received': sent_received_html_table_pair,
            'latency': latency_html_table_pair,
            'resource': resource_html_table_pair,
        }

    # Generate Markdown comparing packet losses across various configurations and middlewares.
    rmw_implementations_md = markdown_for_rmw_implementations(experiements_df)
    bandwidths_md = markdown_for_bandwidths(experiements_df)
    message_type_rate_combos_md = markdown_for_message_type_rate_combos(experiements_df)

    md = f"""\
# Comparing RMW Implementations Across Bandwidths and Packet Losses

Comparison is between the rmw implementations {rmw_implementations_md}, and is
varied across bandwidth limits ({bandwidths_md}) and message type/rate
combinations ({message_type_rate_combos_md}).

Data was collected using the `run_experiments.py` script, and uses [mininet](http://mininet.org/)
to simulate adverse network conditions, potentially varying the bandwidth limit, packet loss,
and/or packet delay for each process.

Each experimental run consists of two processes, one containing a publisher and the other
containing a subscription.
Experiments are run for 15 seconds, and various statistics are collected, but for this
comparison only "number of messages sent/received per second" are considered.

"""
    pandoc_friendly_md = md
    # Start with Bandwidth, then select by message type and message rate.
    df_groupby_bandwidth = experiements_df.groupby(['bandwidth'])
    for bw_group, bw_indexes in df_groupby_bandwidth.groups.items():
        next_md = f"""\
## Comparisons with Bandwidth Limited to {bw_group}Mbps

"""
        md += next_md
        pandoc_friendly_md += next_md
        df_groupby_message_type_and_rate = \
            experiements_df.loc[bw_indexes].groupby(['message_type', 'message_rate'])
        for mtr_group, mtr_indexes in df_groupby_message_type_and_rate.groups.items():
            mtr_df = experiements_df.loc[mtr_indexes]

            number_of_runs = len(set(mtr_df['run']))
            tmp = mtr_df[['rmw_implementation', 'async_pub']]
            rmw_implementations = set([
                (x['rmw_implementation'], x['async_pub']) for i, x in tmp.iterrows()
            ])
            rmw_implementations = [f'{rmw} {async_pub}' for rmw, async_pub in rmw_implementations]
            rmw_implementations = '/'.join(rmw_implementations)
            message_type = get_one_item(mtr_df, 'message_type')
            message_rate = get_one_item(mtr_df, 'message_rate')
            reliability = get_one_item(mtr_df, 'reliability')
            durability = get_one_item(mtr_df, 'durability')
            history_kind = get_one_item(mtr_df, 'history_kind')
            history_depth = get_one_item(mtr_df, 'history_depth')
            bandwidth = get_one_item(mtr_df, 'bandwidth')
            losses = '/'.join([str(x) for x in sorted(set(mtr_df['loss']))])
            delay = get_one_item(mtr_df, 'delay')
            next_md = f"""\
### Comparison Publishing {mtr_group[0]}@{mtr_group[1]}

The specific details for this experiment are as follows:

- 1 Publisher
- 1 Subscription
- Separate Processes
- Single Machine
- Number of Runs Averaged: {number_of_runs}
- RMW Implementation: {rmw_implementations}
- Message Type: {message_type}
- Message Rate: {message_rate}
- Reliability QoS: {reliability}
- Durability QoS: {durability}
- History Kind QoS: {history_kind}
- History Depth QoS: {history_depth}
- Bandwidth Limit (Mbps): {bandwidth}
- Packet Loss Percentage: {losses}
- Packet Delay (ms): {delay}

"""
            md += next_md
            pandoc_friendly_md += next_md
            # Render the comparison for each rmw implementation.
            df_groupby_rmw = \
                experiements_df.loc[mtr_indexes].groupby(['rmw_implementation', 'async_pub'])
            for rmw_group, rmw_indexes in df_groupby_rmw.groups.items():
                rmw_df = experiements_df.loc[rmw_indexes]
                md += generate_html_table_for_single_config(rmw_df, html_table_pairs_by_directory)
                pandoc_friendly_md += generate_markdown_table_for_single_config(rmw_df, loss_plot_pairs_by_directory)

    # print(md)
    markdown_path = os.path.join(output_dir, 'report.md')
    with open(markdown_path, 'w+') as fp:
        print(f'=== Generating markdown report: {markdown_path}')
        fp.write(md)

    pandoc_path = os.path.join(output_dir, 'report_pandoc.md')
    with open(pandoc_path, 'w+') as fp:
        print(f'=== Generating pandoc friendly markdown report: {pandoc_path}')
        fp.write(pandoc_friendly_md)

    html = markdown.markdown(md)
    html_path = os.path.join(output_dir, 'report.html')
    with open(html_path, 'w+') as fp:
        print(f'=== Generating html report: {html_path}')
        fp.write(html)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--log-dir',
        type=str,
        help='Directory of the performance log data generated with run_experiments.py',
    )
    parser.add_argument(
        '--output-dir',
        default=os.getcwd(),
        type=str,
        help='Directory to output the plots and report into',
    )

    args = parser.parse_args()
    generate_report(args.log_dir, args.output_dir)


if __name__ == '__main__':
    main()
