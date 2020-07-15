from ros:eloquent

# Install mininet
RUN apt update -qq && \
    apt install -y mininet openvswitch-testcontroller iproute2 iputils-ping && \
    apt install -y python3-pip && \
    pip3 install git+https://github.com/mininet/mininet.git && \
    apt clean &&  \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install ROS demo package
RUN apt update -qq && \
    apt install -y ros-eloquent-demo-nodes-cpp && \
    apt clean &&  \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install dev tools
RUN apt update -qq && \
    apt install -y tmux vim && \
    apt clean &&  \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /root

COPY demos demos

COPY entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]

CMD ["bash"]
