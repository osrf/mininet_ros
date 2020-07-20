import time
from typing import List

from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

from .host_options import HostOptions
from .topo import ManyHostsOneSwitchTopo


def emulate_ros_network(
    *,
    host_options: List[HostOptions],
    duration=5.0,
):
    """
    Create an emulated network for running ROS nodes.

    :param hosts_options: A list of host options.
       The length of the list determines the number of hosts in the emulated
       network.
    :param duration: How long to let the commands run on each host.
    """
    # Tell mininet to print useful information
    setLogLevel('info')

    # Create the topology and network
    topo = ManyHostsOneSwitchTopo(num_hosts=len(host_options))
    net = Mininet(topo)
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

    # Let commands run for some duration
    # TODO(jacobperron): or until they have terminated
    start_time = time.time()
    while (time.time() - start_time) < duration:
        time.sleep(0.1)

    # Interrupt commands
    for host in net.hosts:
        host.sendInt()

    # Wait for output
    for host in net.hosts:
        print(f"Host '{host.name}' output:")
        host.waitOutput(verbose=True)

    net.stop()
