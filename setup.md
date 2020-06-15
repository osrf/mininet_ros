Steps followed to install (Ubuntu 18.04):

1. sudo apt install mininet
2. sudo apt install openvswitch-testcontroller

For Python 3 support, intall mininet from Git:

    pip3 install git+https://github.com/mininet/mininet.git

Troubleshooting:

Seems that after installing the test controller, we see an exception looking like:

    Exception: Please shut down the controller which is running on port 6653:

To resolve, we can shut it down with the following command (replacing port number with the same from the exception message):

    sudo fuser -k 6633/tcp

[Reference](https://github.com/mininet/mininet/issues/399)
