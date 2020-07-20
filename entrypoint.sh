#!/usr/bin/env bash
service openvswitch-switch start

. /root/perf_test_ws/install/setup.bash

if [ $# -gt 0 ]; then
  $@
fi
