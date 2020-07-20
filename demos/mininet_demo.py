from mininet.net import Mininet
from mininet.util import dumpNodeConnections

from mininet_ros.topo import ManyHostsOneSwitchTopo


def main():
    """Create and test the network."""
    topo = ManyHostsOneSwitchTopo(num_hosts=2)
    net = Mininet(topo)
    net.start()
    print("Dumping host connections")
    dumpNodeConnections(net.hosts)
    print("Testing network connectivity")
    net.pingAll()
    net.stop()

if __name__ == '__main__':
    main()
