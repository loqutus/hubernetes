#!/usr/bin/env bash
cd etcd
etcd 2>&1 3>&1 >/dev/null &
cd ..
./hubernetes.py