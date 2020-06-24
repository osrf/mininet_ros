import argparse
import time
from typing import List

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel


class TwoNodesOneSwitchTopo(Topo):
    """Single switch connected to two hosts."""
    def build(self):
        switch = self.addSwitch('s1')
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        self.addLink(h1, switch)
        self.addLink(h2, switch)


def emulate_ros_network(
    *,
    ros_setup_bash,
    host_1_cmd: List[str],
    host_2_cmd: List[str],
    duration=5.0,
    ros_domain_id=0
):
    """
    Create an emulated network for running ROS nodes.

    :param ros_setup_bash: Path to the setup.bash file of the ROS installation.
    :param host_1_cmd: The command to run on the first emulated host.
    :param host_2_cmd: The command to run on the second emulated host.
    :param duration: How long to let the commands run.
    :param ros_domain_id: The value to assign to the ROS_DOMAIN_ID environment variable.
    """
    ros_setup_bash = str(ros_setup_bash)
    preamble = ['source', ros_setup_bash, '&&', 'export', f'ROS_DOMAIN_ID={ros_domain_id}']
    host_1_cmd_with_preamble = preamble + ['&&'] + host_1_cmd
    host_2_cmd_with_preamble = preamble + ['&&'] + host_2_cmd

    # Create the topology and network
    topo = TwoNodesOneSwitchTopo()
    net = Mininet(topo)
    net.start()
    print("Dumping host connections")
    dumpNodeConnections(net.hosts)
    # This is recommended for bootstrapping the network controller
    print("Testing network connectivity")
    net.pingAll()

    host_1 = net.hosts[0]
    host_2 = net.hosts[1]

    # Run command on the first host
    print(f"Running command on host 1: {' '.join(host_1_cmd_with_preamble)}")
    host_1.sendCmd(host_1_cmd_with_preamble)

    # Run command on the second host
    print(f"Running command on host 2: {' '.join(host_2_cmd_with_preamble)}")
    host_2.sendCmd(host_2_cmd_with_preamble)

    # Let commands run for some duration
    # TODO(jacobperron): or until they have terminated
    start_time = time.time()
    while (time.time() - start_time) < duration:
        time.sleep(0.1)

    # Interrupt commands
    host_1.sendInt()
    host_2.sendInt()

    # Wait for output
    print('Host 1 output:')
    host_1.waitOutput(verbose=True)
    print('Host 2 output:')
    host_2.waitOutput(verbose=True)

    net.stop()


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'ros_setup_bash',
        nargs='?',
        default='/opt/ros/eloquent/setup.bash',
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

    # Tell mininet to print useful information
    setLogLevel('info')

    emulate_ros_network(
        ros_setup_bash=args.ros_setup_bash,
        host_1_cmd=['ros2', 'run', 'demo_nodes_cpp', 'talker'],
        host_2_cmd=['ros2', 'run', 'demo_nodes_cpp', 'listener'],
        duration=args.duration,
        ros_domain_id=args.ros_domain_id,
    )
