#!/bin/bash

# # Design scripts
current_dir=$(pwd)
echo "Running Instances Bomb Problems"
for i in 001 002 005 010 020 030 040 050 060 070 080 090 100 110 120 130 140 150
do
    echo "cat ${current_dir}/benchmarks/qasp/bomb_problems/bt_base.lp ${current_dir}/benchmarks/qasp/bomb_problems/bt.lp ${current_dir}/benchmarks/eclingo/bomb_problems/instances/bomb_0${i}.lp | ${current_dir}/benchmark-tool/programs/elp-qasp-bomb" > ${current_dir}/benchmarks/qasp/bomb_problems/instances/bt/bt_bomb_0${i}.sh
    echo "Done bt/bt_bomb_00${i}"

    echo "cat ${current_dir}/benchmarks/qasp/bomb_problems/bt_base.lp ${current_dir}/benchmarks/qasp/bomb_problems/btc.lp ${current_dir}/benchmarks/eclingo/bomb_problems/instances/bomb_0${i}.lp | ${current_dir}/benchmark-tool/programs/elp-qasp-bomb" > ${current_dir}/benchmarks/qasp/bomb_problems/instances/btc/btc_bomb_0${i}.sh
    echo "Done btc/btc_bomb_00${i}"

    echo "cat ${current_dir}/benchmarks/qasp/bomb_problems/bt_base.lp ${current_dir}/benchmarks/qasp/bomb_problems/btuc.lp ${current_dir}/benchmarks/eclingo/bomb_problems/instances/bomb_0${i}.lp | ${current_dir}/benchmark-tool/programs/elp-qasp-bomb" > ${current_dir}/benchmarks/qasp/bomb_problems/instances/btuc/btuc_bomb_0${i}.sh
    echo "Done btuc/btuc_bomb_00${i}"
done
echo "DONE Instances Bomb Problems"

echo "Running Many Bomb Problems"
for i in 010 020 030 040 050 060 070 080 090 100 110 120 130 140 150
do
    for j in 1 2 3 4
    do  
        echo "cat ${current_dir}/benchmarks/qasp/bomb_problems/bt_base.lp ${current_dir}/benchmarks/qasp/bomb_problems/bmtc.lp ${current_dir}/benchmarks/eclingo/bomb_problems/instances_many/bomb_0${i}_0${j}.lp | ${current_dir}/benchmark-tool/programs/elp-qasp-bomb" > ${current_dir}/benchmarks/qasp/bomb_problems/instances_many/bmtc/bmtc_bomb_0${i}_0${j}.sh
        echo "Done many_bmtc ${i}_${j}"

        echo "cat ${current_dir}/benchmarks/qasp/bomb_problems/bt_base.lp ${current_dir}/benchmarks/qasp/bomb_problems/bmtuc.lp ${current_dir}/benchmarks/eclingo/bomb_problems/instances_many/bomb_0${i}_0${j}.lp | ${current_dir}/benchmark-tool/programs/elp-qasp-bomb" > ${current_dir}/benchmarks/qasp/bomb_problems/instances_many/bmtuc/bmtuc_bomb_0${i}_0${j}.sh
        echo "Done many_bmtuc ${i}_${j}"
    done
done
echo "Many Bomb Problems Done"

# Create Yale instances
echo "Running Instances Yale Problems"
for i in 1 2 3 4 5 7 8
do
    echo "cat ${current_dir}/benchmarks/qasp/yale_problems/sp/yale${i}.sp | ${current_dir}/benchmark-tool/programs/elp-qasp-yale" > ${current_dir}/benchmarks/qasp/yale_problems/yale_${i}.sh
    echo "Done yale_${i}.sp"
done


# Create Eligible instances
echo "Running Instances Eligible Problems"
for i in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25
do
    cat ${current_dir}/benchmarks/qasp/eligible/eligible_qasp.lp ${current_dir}/benchmarks/eclingo/eligible/input/eligible${i}.lp > ${current_dir}/benchmarks/qasp/eligible/input/eligible_qasp${i}.lp
    echo "ulimit -t 600 && cat ${current_dir}/benchmarks/qasp/eligible/input/eligible_qasp${i}.lp | ${current_dir}/benchmark-tool/programs/elp-qasp" > ${current_dir}/benchmarks/qasp/eligible/scripts/eligible_qasp${i}.sh
    echo "Done eligible_${i}.aspq"
done

Create new-eligible
Define the directory for new-Eligible
DIR="${current_dir}/benchmarks/new_eligible"

# Extract the XXXX numbers from the filenames
numbers=($(ls $DIR | grep -oP 'eligible\K[0-9]{4}(?=-1.lp)'))

# Iterate over the numbers
for number in "${numbers[@]}"; do
    echo "Processing eligible file number: $number"
    echo "ulimit -t 600 && cat ${current_dir}/benchmarks/qasp/eligible/new/eligible$number-1.lp | ${current_dir}/benchmark-tool/programs/elp-qasp" > ${current_dir}/benchmarks/qasp/eligible/scripts/eligible_qasp_$number-1.sh
done

