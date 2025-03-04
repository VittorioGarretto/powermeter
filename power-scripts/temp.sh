#!/bin/bash

PHY_TEMP=$(sensors | awk -F'[:+°C]+' '/PHY Temperature/ {print $3}')
MAC_TEMP=$(sensors | awk -F'[:+°C]+' '/MAC Temperature/ {print $4}')
TCTL=$(sensors | awk -F'[:+°C]+' '/Tctl/ {print $3}')
TCCD1=$(sensors | awk -F'[:+°C]+' '/Tccd1/ {print $3}')
TCCD3=$(sensors | awk -F'[:+°C]+' '/Tccd3/ {print $3}')
TCCD5=$(sensors | awk -F'[:+°C]+' '/Tccd5/ {print $3}')
TCCD7=$(sensors | awk -F'[:+°C]+' '/Tccd7/ {print $3}')

echo $PHY_TEMP,$MAC_TEMP,$TCTL,$TCCD1,$TCCD3,$TCCD5,$TCCD7