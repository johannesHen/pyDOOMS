#!/bin/bash
MONTY=""
TEST=""
totaltime=0
verbose=false
file="monte_carlo.py"

while getopts "vf:" opt; do
  case $opt in
    v)
	  verbose=true
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
echo "Looping monte_carlo.py $1 times with $2 processes"


commandStrNumberOfLoops=$(echo $2 - 1 | bc)

if [ $2 -lt 2 ]
then
	commandStr="mpiexec -np 1 python 0.0/tests/$file 0 1"
else	
	commandStr="mpiexec -np 1 python 0.0/tests/$file 0 $2"
fi

if [ $2 -gt 1 ]
then
	for x in `seq 1 $commandStrNumberOfLoops`; 
	do
	tempCommandStr=": -np 1 python 0.0/tests/$file $x $2"
	commandStr="$commandStr $tempCommandStr"
	done
	
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
