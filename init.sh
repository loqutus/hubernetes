#!/usr/bin/env bash
./start.sh &
etcdctl mkdir /hubernetes
etcdctl set /hubernetes/docker_hosts '{"localhost": "unix://var/run/docker.sock"}'