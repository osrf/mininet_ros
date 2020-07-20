from mininet.topo import Topo


class ManyHostsOneSwitchTopo(Topo):
    """Single switch connected to multiple hosts."""

    def __init__(self, *, num_hosts: int):
        """
        Constructor.

        :param num_hosts: The number of hosts connected to the switch.
           The names of the hosts will be 'h1', 'h2', ..., 'hN' where N is the
           number of hosts.
        """
        self.__num_hosts = num_hosts
        super().__init__()

    def build(self):
        switch = self.addSwitch('s1')
        for n in range(1, self.__num_hosts + 1):
            host = self.addHost(f'h{n}')
            self.addLink(host, switch)
