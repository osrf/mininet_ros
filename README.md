# Mininet + ROS 2 demonstration

Dockerfile with examples running ROS 2 nodes on emulated hosts.
Potentially useful for testing and benchmarking ROS 2 communication between multiple hosts under different network contraints and topologies.

## Run demos with Docker (Ubuntu)

Start a Docker container with the `--privileged` option.
Ensure the Docker image is using the same version of Ubuntu as your local host.

| Host OS | Docker image |
|---------|--------------|
| Ubuntu 18.04 | jacobperron/mininet_ros_demo:eloquent |
| Ubuntu 20.04 | jacobperron/mininet_ros_demo:foxy |


    docker run -it --privileged jacobperron/mininet_ros_demo:eloquent

Run the demos with `python3`.

Vanilla mininet demo:

    python3 mininet_demo.py

ROS talker/listener demo:

    python3 mininet_ros_demo_,py


## Run demos without Docker


1. Install mininet

    sudo apt install mininet

2. Install `openvswitch-testcontroller`

    sudo apt install openvswitch-testcontroller

3. For Python 3 support, also install mininet from Git:

    pip3 install git+https://github.com/mininet/mininet.git


#### Troubleshooting

Seems that after installing the test controller, we see an exception looking like:

    Exception: Please shut down the controller which is running on port 6653:

To resolve, we can shut it down with the following command (replacing port number with the same from the exception message):

    sudo fuser -k 6633/tcp

[Reference](https://github.com/mininet/mininet/issues/399)
