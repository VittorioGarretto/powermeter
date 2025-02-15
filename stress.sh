#!/bin/bash

ITERATIONS=50
batch=1
cicle=1

while true; do
    for ((i=1; i<=ITERATIONS; i++))
    do
        echo "Iteration $i: Stress test on GPU"
        python3 ../stress_test.py --gpu_id 0 --batch "$batch"
        
        echo "Iteration $i: 8 seconds cool down"
        sleep 8
        batch=$((batch + 10))
    done
    echo "Cicle $cicle done"
    batch=1
    cicle=$((cicle + 1))
    sleep 20
done