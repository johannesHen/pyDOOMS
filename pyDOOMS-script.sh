#!/bin/bash
MONTY=""
TEST=""
for i in `seq 1 10`;
do
mpiexec -np 1 python ~/Documents/workspace/ProjektIT/pyDOOMS/0.0/monte_carlo.py 0 \
: -np 1 python ~/Documents/workspace/ProjektIT/pyDOOMS/0.0/monte_carlo.py 1 \
: -np 1 python ~/Documents/workspace/ProjektIT/pyDOOMS/0.0/monte_carlo.py 2 \
: -np 1 python ~/Documents/workspace/ProjektIT/pyDOOMS/0.0/monte_carlo.py 3
done