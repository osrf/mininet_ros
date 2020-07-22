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

    python3 demos/mininet_demo.py

ROS talker/listener demo:

    python3 demos/mininet_ros_demo.py

ROS performance test demo:

    # Provide --help option for usage
    python3 demos/mininet_ros_perf_demo.py


## Run demos without Docker

1. Install mininet
  - Ubuntu 18.04

        sudo apt install mininet
        sudo apt install openvswitch-testcontroller
        pip3 install git+https://github.com/mininet/mininet.git

  - Ubuntu 20.04

        # Install mininet from source (use at own risk)
        git clone http://github.com/mininet/mininet.git
        cd mininet
        util/install.sh -fnv

2. Clone this repository

    git clone https://github.com/jacobperron/mininet_ros_demos.git

3. Run the demos with Python 3, for example

    python3 mininet_ros_demos/demos/mininet_ros_demo.py

#### Troubleshooting

Seems that after installing the test controller, we see an exception looking like:

    Exception: Please shut down the controller which is running on port 6653:

To resolve, we can shut it down with the following command (replacing port number with the same from the exception message):

    sudo fuser -k 6633/tcp

[Reference](https://github.com/mininet/mininet/issues/399)
