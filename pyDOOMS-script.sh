#!/bin/bash
MONTY=""
TEST=""
totaltime=0
verbose=false
file="monte_carlo_proc.py"

while getopts "vf:" opt; do
  case $opt in
    v)
	  verbose=true
      ;;
    f)
	  file=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

shift $(($OPTIND - 1))
echo "Looping monte_carlo_proc.py $1 times with $2 nodes and $3 workers per node"


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
#test1=$(mpiexec -np 1 python 0.0/tests/monte_carlo.py 0 : -np 1 python 0.0/tests/monte_carlo.py 1 : -np 1 python 0.0/tests/monte_carlo.py 2 : -np 1 python 0.0/tests/monte_carlo.py 3)
echo $test1

totaltime=$(echo $totaltime + $test1 | bc)
done

totaltime=totaltime | bc

averagetime=$(echo $totaltime / $1 | bc -l)

#echo $totaltime 
echo "Average calculation time is: $averagetime seconds"
