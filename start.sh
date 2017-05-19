#!/usr/bin/env bash
set -x
pkill etcd
cd etcd
etcd 2>/dev/null >/dev/null &
cd ..
sleep 1
etcdctl mkdir /hubernetes
etcdctl set /hubernetes/hosts '{"localhost": "unix://var/run/docker.sock"}'
etcdctl set /hubernetes/images '["alpine:latest"]'
etcdctl set /hubernetes/groups '{"test":{"image":"alpine:latest", "instances":"4", "command":"/bin/sleep 60"}}'
./hubernetes.py