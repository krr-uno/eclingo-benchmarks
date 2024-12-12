#!/bin/bash

# $1:  name of the experiment
name=$1

# set this
dir=$PWD
parentdir="$(dirname "$dir")"
btool=$parentdir

# this has to be the same as project name in run-benchmark.xml
project=project

# this has to be the command used in run-benchmark.xml
command=$PWD/solver.sh
echo "$PWD"
# set mode: sequential=1 or cluster=2
mode=1

# if mode==2, set username to your login in the cluster
username=""

# email to send the results
email=""

bench=$dir/run-benchmark.xml

echo "Start execution..."
rm -rf $dir/results/$name
mkdir -p $dir/results/$name 

# $btool -> running/benchmark-tool-eclingo/experiments
cd $btool

rm -rf output/$project

# $bench -> running/benchmark-tool-eclingo/experiments/run-benchmark.xml
echo "Generating Scripts -> bgen..."
./bgen $bench

sleep 1

if [ $mode -eq 1 ]; then
    echo "$btool/output/$project/zuse/start.py..."
    python2 ./output/$project/zuse/start.py
else
    echo "$btool/output/$project/zuse/start.sh..."
    python2 ./output/$project/zuse/start.sh
    while squeue | grep -q $username; do
        sleep 1
    done
fi


echo "Evaluating -> beval..."
./beval $bench > $dir/results/$name/$name.beval 2> $dir/results/$name/$name.error

echo "Converting evaluation -> bconv..."
cat $dir/results/$name/$name.beval | ./bconv -m time,ctime,csolve,ground0,groundN,models,timeout,restarts,conflicts,choices,domain,vars,cons,mem,error,memout > $dir/results/$name/$name.ods 2>> $dir/results/$name/$name.error

echo "tar..."
tar -czf $name.tar.gz output/$project
mv $name.tar.gz $dir/results/$name
cp $bench $dir/results/$name
cp $command $dir/results/$name
# rm -rf output/$project

echo "Spreadsheet results at: $dir/results/$name/$name.ods"
# send an email to report that the experiments are done
# echo "done $1" | mail -s "[benchmark_finished] $1 " -A $dir/results/$name/$name.ods $email
echo "done $1" 
# | mail -s "[benchmark_finished] $1" $email -A $dir/results/$name/$name.ods 

