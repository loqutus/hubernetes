#!/usr/bin/env bash
set -x
for i in $(seq 2 5); do
  ssh root@pi$i reboot
done
sleep 5
sudo reboot
