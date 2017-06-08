#!/usr/bin/env bash
set -x
> hubernetes.log
etcdctl mkdir /hubernetes
etcdctl set /hubernetes/hosts '{"pi1": "pi1:7777", "pi2": "pi2:7777", "pi3": "pi3:7777", "pi4": "pi4:7777", "pi5": "pi5:7777"}'
etcdctl set /hubernetes/images '["sleep"]'
etcdctl set /hubernetes/groups '{"test1":{"image":"sleep", "instances":"5", "command":"/bin/sleep 60"}}'
./hubernetes.py
