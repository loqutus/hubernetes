#!/usr/bin/env bash
for i in $(seq 1 5); do
  echo pi$i
  ssh pi$i 'pkill -f burnCortexA9 &'
  ssh pi$i '/usr/local/bin/burn.sh' &
done
while true; do
  for i in $(seq 1 5); do 
    echo -n "pi$i: "
    ssh root@pi$i /usr/local/bin/temp.sh
  done
  sleep 2
  clear
done
