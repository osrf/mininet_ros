from ros:foxy

WORKDIR /root

# Install mininet
# Build from source since upstream version in Ubuntu is not working
RUN apt update -qq && \
    apt install -y git iputils-ping && \
    git clone http://github.com/mininet/mininet.git && \
    cd mininet && \
    util/install.sh -fnv && \
    apt clean &&  \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install more RMW implementations
RUN apt update -qq && \
    RTI_NC_LICENSE_ACCEPTED=yes apt install -y ros-${ROS_DISTRO}-rmw-cyclonedds-cpp ros-${ROS_DISTRO}-rmw-connext-cpp && \
    apt clean &&  \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install ROS 2 performance_test package
RUN apt update -qq && \
    apt install -y default-jre && \
    mkdir -p perf_test_ws/src && \
    cd perf_test_ws && \
    git clone https://github.com/ros2/performance_test.git src/performance_test && \
    . /opt/ros/foxy/setup.sh && \
    rosdep install -y --from-paths src --ignore-src && \
    colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release && \
    apt clean &&  \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install ROS demo package
RUN apt update -qq && \
    apt install -y ros-foxy-demo-nodes-cpp && \
    apt clean &&  \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install dev tools
RUN apt update -qq && \
    apt install -y tmux vim && \
    apt clean &&  \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY demos demos

COPY entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]

CMD ["bash"]
