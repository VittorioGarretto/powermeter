#!/bin/bash

# Numero di iterazioni
ITERATIONS=2  

for ((i=1; i<=ITERATIONS; i++))
do
    echo "Iterazione $i: Stress test sulla GPU"
    python3 stress_test.py
    
    echo "Iterazione $i: Attesa di 20 secondi per il raffreddamento"
    sleep 20
done

echo "Test completato."