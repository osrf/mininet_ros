from functools import partial
import time
from typing import List

from mininet.link import TCLink
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

from .host_options import HostOptions
from .topo import ManyHostsOneSwitchTopo


def _waiting(hosts):
    for host in hosts:
        if host.waiting:
            return True
    return False


def emulate_ros_network(
    *,
    host_options: List[HostOptions],
    duration=None,
    verbose=False,
    bandwidth=None,
    loss=0,
    delay=0,
):
    """
    Create an emulated network for running ROS nodes.

    :param hosts_options: A list of host options.
       The length of the list determines the number of hosts in the emulated
       network.
    :param duration: How long to let the commands run on each host.
      If None, then run the commands until they complete.
    :param verbose: Prints interleaved command output from all hosts to the
      screen.
    :param bandwidth: Bandwidth in Mb/s between each pair of hosts.
      None for no limit.
    :param loss: Packet loss percentage between each pair of hosts (0-100).
    :param delay: Adds delay to traffic between each pair of hosts (milliseconds).
    """
    # Tell mininet to print useful information
    setLogLevel('info')

    # Create the topology and network
    topo = ManyHostsOneSwitchTopo(num_hosts=len(host_options))
    link = partial(TCLink, bw=bandwidth, loss=loss, delay=f'{delay}ms')
    net = Mininet(topo=topo, link=link)
    net.start()
    print("Dumping host connections")
    dumpNodeConnections(net.hosts)
    # This is recommended for bootstrapping the network controller
    print("Testing network connectivity")
    net.pingAll()

    # Run commands for each host
    for host, options in zip(net.hosts, host_options):
        print(f"Running command on host '{host.name}': {' '.join(options.command)}")
        host.sendCmd(options.command)

    if duration is not None:
        start_time = time.time()

    hosts_output = [''] * len(net.hosts)
    interrupted = False
    # Wait until commands have complete
    while _waiting(net.hosts):
        # Collect output
        for i, host in enumerate(net.hosts):
            output = host.monitor(10)
            hosts_output[i] += output
            if verbose:
                print(output)

        # We already interrupted the processes, just waiting for remaining output
        if interrupted:
            continue

        # Check for timeout and interrupt commands
        if duration is not None and (time.time() - start_time) >= duration:
            print('Timed out, interrupting commands')
            for host in net.hosts:
                host.sendInt()
            interrupted = True

    for host, output in zip(net.hosts, hosts_output):
        print(f"Host '{host.name}' output:\n{output}")

    net.stop()
