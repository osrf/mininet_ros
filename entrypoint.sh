#!/usr/bin/env bash
service openvswitch-switch start

if [ $# -gt 0 ]; then
  $@
fi
