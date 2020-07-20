from mininet.net import Mininet
from mininet.util import dumpNodeConnections

from mininet_ros.emulate_network import TwoNodesOneSwitchTopo


def main():
    """Create and test the network."""
    topo = TwoNodesOneSwitchTopo()
    net = Mininet(topo)
    net.start()
    print("Dumping host connections")
    dumpNodeConnections(net.hosts)
    print("Testing network connectivity")
    net.pingAll()
    net.stop()

if __name__ == '__main__':
    main()
