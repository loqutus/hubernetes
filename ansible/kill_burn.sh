#!/usr/bin/env bash
for i in $(seq 1 5); do 
  ssh root@pi$i killall -9 burnCortexA9
done
