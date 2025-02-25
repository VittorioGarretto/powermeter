#!/bin/bash

isActive() {
    device=$(echo "$1" | cut -d "/" -f3)
    stats0=$(</sys/block/$device/stat)
    sleep .1s
    stats1=$(</sys/block/$device/stat)
    if [[ "$stats0" == "$stats1" ]]; then
        echo "inactive"
    else
        echo "active"
    fi
}

activityModifier() {
    if [[ $(isActive $1) == "active" ]]; then
        echo 1.
        return 0
    fi
    echo 0.2
    return 0
}

export ELEMENTO_POWER_NVME=0
NVME_DEVICES=$(nvme list | tail -n +3 | awk '{print $1}')

while IFS= read -r dev; do
    if [[ ! -z "$dev" ]]
    then
        power_states=( $(smartctl -a "$dev" | sed -n '/Supported Power States/,/^ *$/p' | head -n -1 | tail -n +3 | grep -Eo '[+-]?[0-9]+([.][0-9]+)?W') )
        power_state=$(nvme get-feature "$dev" -f 2 -H | tail -1 | grep -o [0-9])
        state=$(hdparm -C $dev | grep -e "drive state is:" | cut -d ":" -f2 | tr -d ' ')
        modifier=1.
        case $state in
            "unknown")
                modifier=$(activityModifier $dev)
                ;;
            "active/idle")
                modifier=$(activityModifier $dev)
                ;;
            "standby")
                modifier=.2
                ;;
            "sleeping")
                modifier=.1
                ;;
        esac
        devicepower=$(echo "${power_states[$power_state]} * $modifier" | bc)
        ELEMENTO_POWER_NVME=$(echo "$ELEMENTO_POWER_NVME + $devicepower" | bc)
    fi
done <<< "$NVME_DEVICES"

echo $ELEMENTO_POWER_NVME