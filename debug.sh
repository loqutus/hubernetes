#!/usr/bin/env bash
set -x
> hubernetes.log
etcdctl mkdir /hubernetes
etcdctl set /hubernetes/hosts '[{"pi1": "pi1:7777"}]'
etcdctl set /hubernetes/images '["sleep"]'
etcdctl set /hubernetes/groups '{"test1":{"image":"sleep", "instances":"1", "command":"/bin/sleep 60"}}'
./hubernetes.py
