from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

class TwoNodesOneSwitchTopo(Topo):
    """Single switch connected to two hosts."""
    def build(self):
        switch = self.addSwitch('s1')
        host_1 = self.addHost('h1')
        host_2 = self.addHost('h2')
        self.addLink(host_1, switch)
        self.addLink(host_2, switch)

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
    # Tell mininet to print useful information
    setLogLevel('info')
    main()
