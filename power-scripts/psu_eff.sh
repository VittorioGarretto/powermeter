#!/bin/bash

LOAD=$1
MAX_LOAD=${2:-"850"}

LOAD_PC=`bc -l <<< "$LOAD / $MAX_LOAD * 100"`
EFFICIENCY=${3:-"Platinum"}
EFFICIENCY=$(echo "$EFFICIENCY" | tr '[:upper:]' '[:lower:]')

declare -A EFFCURVES
EFFCURVES[base]="0, 0, 80"
EFFCURVES[bronze]="-0.0354, 2.58, 44.571"
EFFCURVES[silver]="-0.0367, 2.67, 46.286"
EFFCURVES[gold]="-0.0376, 2.73, 47.429"
EFFCURVES[platinum]="-0.00158, 0.1775, 87.0833"
EFFCURVES[titanium]="-0.0405, 2.90, 52.190"

readarray -td, P <<<"${EFFCURVES[$EFFICIENCY]}"

ELEMENTO_PSU_EFFICIENCY=`bc -l <<< "${P[0]} * $LOAD_PC * $LOAD_PC + ${P[1]} * $LOAD_PC + ${P[2]}"`

# if (( $(echo "$ELEMENTO_PSU_EFFICIENCY <= 80" |bc -l) )); then
#     ELEMENTO_PSU_EFFICIENCY=80
# fi


ELEMENTO_PSU_EFFICIENCY=`bc -l <<< "scale=4; $ELEMENTO_PSU_EFFICIENCY / 100"`

echo $ELEMENTO_PSU_EFFICIENCY