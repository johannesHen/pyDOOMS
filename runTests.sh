#!/bin/bash
file="test.py"

echo "Looping test.py $1 times with $2 nodes and $3 workers per node"

commandStrNumberOfLoops=$(echo $2 - 1 | bc)

if [ $2 -lt 2 ]
then
	commandStr="mpiexec -np 1 python multiprocess/tests/$file 1 $3"
else
	commandStr="mpiexec -np $2 python multiprocess/tests/$file $2 $3"
fi


echo $commandStr

for i in `seq 1 $1`;
do
test1=$($commandStr)
echo $test1

done