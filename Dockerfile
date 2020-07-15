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
