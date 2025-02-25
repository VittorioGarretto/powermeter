#! /bin/bash
cmd="sudo perf stat -a -e power/energy-pkg/ sleep 0.5 2>&1 | head -4 | tail -1 | awk '{print \$1}'"

export POWER_CPU

joules=$(eval $cmd)
POWER_CPU=$(echo "scale=2; ($joules) / .5" | bc)

echo $POWER_CPU