#!/bin/bash

# Execute it from base directory -> eclingo-benchmark
current_dir=$(pwd)

echo "Creating scripts for BOMB"
for i in 001 002 005 010 020 030 040 050 060 070 080 090 100 110 120 130 140 150
do
    echo "cat ${current_dir}/benchmarks/qasp/bomb_problems/bt_base.lp ${current_dir}/benchmarks/qasp/bomb_problems/bt.lp ${current_dir}/benchmarks/eclingo/bomb_problems/instances/bomb_0${i}.lp | ${current_dir}/benchmark-tool/programs/selp" > ${current_dir}/benchmarks/selp/bomb_problems/instances/bt/bt_bomb_0${i}.sh
    echo "Done bt/bt_bomb_00${i}"

    echo "cat ${current_dir}/benchmarks/qasp/bomb_problems/bt_base.lp ${current_dir}/benchmarks/qasp/bomb_problems/btc.lp ${current_dir}/benchmarks/eclingo/bomb_problems/instances/bomb_0${i}.lp | ${current_dir}/benchmark-tool/programs/selp" > ${current_dir}/benchmarks/selp/bomb_problems/instances/btc/btc_bomb_0${i}.sh
    echo "Done btc/btc_bomb_00${i}"

    echo "cat ${current_dir}/benchmarks/qasp/bomb_problems/bt_base.lp ${current_dir}/benchmarks/qasp/bomb_problems/btuc.lp ${current_dir}/benchmarks/eclingo/bomb_problems/instances/bomb_0${i}.lp | ${current_dir}/benchmark-tool/programs/selp" > ${current_dir}/benchmarks/selp/bomb_problems/instances/btuc/btuc_bomb_0${i}.sh
    echo "Done btuc/btuc_bomb_00${i}"
done
echo "Finished Bomb Instances"

echo "Running Many Bomb Problems"
for i in 010 020 030 040 050 060 070 080 090 100 110 120 130 140 150
do
    for j in 1 2 3 4
    do  
        echo "cat ${current_dir}/benchmarks/qasp/bomb_problems/bt_base.lp ${current_dir}/benchmarks/qasp/bomb_problems/bmtc.lp ${current_dir}/benchmarks/eclingo/bomb_problems/instances_many/bomb_0${i}_0${j}.lp | ${current_dir}/benchmark-tool/programs/selp" > ${current_dir}/benchmarks/selp/bomb_problems/instances_many/bmtc/bmtc_bomb_0${i}_0${j}.sh
        echo "Done many_bmtc ${i}_${j}"

        echo "cat ${current_dir}/benchmarks/qasp/bomb_problems/bt_base.lp ${current_dir}/benchmarks/qasp/bomb_problems/bmtuc.lp ${current_dir}/benchmarks/eclingo/bomb_problems/instances_many/bomb_0${i}_0${j}.lp | ${current_dir}/benchmark-tool/programs/selp" > ${current_dir}/benchmarks/selp/bomb_problems/instances_many/bmtuc/bmtuc_bomb_0${i}_0${j}.sh
        echo "Done many_bmtuc ${i}_${j}"
    done
done
echo "Many Bomb Problems Done"

! IMPORTANT MAKE SURE TO HAVE GRINGO AND CLINGO UNDER YOUR RESPECTIVE CONDA ENVIRONMENT.
echo "Creating scripts for SELP"
echo "Running Instances Eligible Problems"
for i in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25
do
    echo "cat ${current_dir}/benchmarks/selp-benchmarks/eligibleK/eligible${i}.elps | ${current_dir}/benchmark-tool/programs/elp-selp" > benchmarks/selp/eligibleK/eligible${i}.sh
    echo "Done eligible${i}"
done
echo "Finish Eligible instances script creation"

echo "Creating scripts for SELP"
# Create new-eligible
# Define the directory for new-Eligible
DIR="${current_dir}/benchmarks/selp-benchmarks/newEligibleK"

# Extract the XXXX numbers from the filenames
numbers=($(ls $DIR | grep -oP 'eligible\K[0-9]{4}(?=-1.elps)'))

# Iterate over the numbers
for number in "${numbers[@]}"; do
    echo "Processing eligible file number: $number"
    echo "cat ${current_dir}/benchmarks/selp-benchmarks/newEligibleK/eligible$number-1.elps | ${current_dir}/benchmark-tool/programs/elp-selp" > benchmarks/selp/eligibleK/newEligible$number.sh
done

echo "Running Instances Yale Problems"
for i in 1 2 3 4 5 7 8
do
    echo "cat ${current_dir}/benchmarks/selp-benchmarks/simpleYale/yale${i}.sp | ${current_dir}/benchmark-tool/programs/yale-selp" > benchmarks/selp/simpleYale/yale${i}.sh
    echo "Done yale${i}"
done
echo "Finish Yale instances script creation"