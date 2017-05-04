#!/usr/bin/env bash
pkill etcd
cd etcd
etcd 2>/dev/null >/dev/null &
cd ..
./hubernetes.py