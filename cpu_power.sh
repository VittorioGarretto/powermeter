#! /bin/bash
cmd="sudo perf stat -a -e power/energy-pkg/ sleep 0.5 2>&1 | head -4 | tail -1 | awk '{print \$1}'"

export ELEMENTO_POWER_CPU

joules=$(eval $cmd)
ELEMENTO_POWER_CPU=$(echo "scale=4; ($joules) / .5" | bc)

echo $ELEMENTO_POWER_CPU