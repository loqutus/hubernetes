#!/usr/bin/env bash
set -x
> hubernetes.log
pkill etcd
cd etcd
etcd 2>/dev/null >/dev/null &
cd ..
sleep 1
etcdctl mkdir /hubernetes
etcdctl set /hubernetes/hosts '{"localhost": "unix://var/run/docker.sock"}'
etcdctl set /hubernetes/images '["alpine:latest"]'
etcdctl set /hubernetes/groups '{"test1":{"image":"alpine:latest", "instances":"10", "command":"/bin/sleep 60"}, "test2":{"image":"alpine:latest", "instances":"10", "command":"/bin/sleep 60"}}'
./hubernetes.py