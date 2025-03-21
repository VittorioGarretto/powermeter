#!/bin/bash

cmd="sudo ipmitool sdr | awk -F'|' '\$2 ~ /[0-9]/ && \$2 !~ /0x01|0x04/ {gsub(/[^0-9.]/, \"\", \$2); print \$2}' | paste -sd \",\""
TEMP=$(eval $cmd)

echo $TEMP