#!/bin/bash
MONTY=""
TEST=""
totaltime=0

#test2="2"
#test1=test1 | bc
#let "test2 += test2"
#echo $test2

echo "Looping monte_carlo.py $1 times with $2 processes"


commandStrNumberOfLoops=$(echo $2 - 1 | bc)

if [ $2 -lt 2 ]
then
	commandStr="mpiexec -np 1 python 0.0/monte_carlo.py 0 1"
else	
	commandStr="mpiexec -np 1 python 0.0/monte_carlo.py 0 $2"
fi

if [ $2 -gt 1 ]
then
	for x in `seq 1 $commandStrNumberOfLoops`; 
	do
	tempCommandStr=": -np 1 python 0.0/monte_carlo.py $x $2"
	commandStr="$commandStr $tempCommandStr"
	done
	
fi


echo $commandStr

for i in `seq 1 $1`;
do
test1=$($commandStr)
#test1=$(mpiexec -np 1 python 0.0/monte_carlo.py 0 : -np 1 python 0.0/monte_carlo.py 1 : -np 1 python 0.0/monte_carlo.py 2 : -np 1 python 0.0/monte_carlo.py 3)
echo $test1

totaltime=$(echo $totaltime + $test1 | bc)
done

totaltime=totaltime | bc

averagetime=$(echo $totaltime / $1 | bc -l)

#echo $totaltime 
echo "Average calculation time is: $averagetime seconds"
