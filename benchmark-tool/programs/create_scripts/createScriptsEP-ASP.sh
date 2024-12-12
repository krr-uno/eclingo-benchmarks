#!/bin/bash

# Need to include the file within the EP-ASP folder to be able to run it.

# Instances bomb_0xxx
current_dir=$(pwd)

echo "Running Instances Bomb Problems"
for i in 1 2 5 10 20 30 40 50 60 70 80 90 100 110 120 130 140 150
do
    np_len=$((i / 2))
    
    echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/bt_conf.lp -c np=${i} -c len=1 -c length=${i} -c planning=1 -c heuristic=1 -c debug=0 -c initials_only=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp/bombProblems/instances/bt/bt_bomb_0${i}.sh
    echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/bt_conf_np.lp -c np=${i} -c len=1 -c length=${i} -c planning=0 -c heuristic=0 -c debug=0 -c initials_only=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp_no_planning/bombProblems/instances/bt/bt_bomb_0${i}.sh
    chmod -x benchmarks/ep_asp/bombProblems/instances/bt/bt_bomb_0${i}.sh
    chmod -x benchmarks/ep_asp_no_planning/bombProblems/instances/bt/bt_bomb_0${i}.sh
    echo "Done bt ${i}"

    echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/btc_conf.lp -c np=$np_len -c len=1 -c length=${i} -c planning=1 -c heuristic=1 -c debug=0 -c initials_only=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp/bombProblems/instances/btc/btc_bomb_0${i}.sh
    echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/btc_conf_np.lp -c np=$np_len -c len=1 -c length=${i} -c planning=0 -c heuristic=0 -c debug=0 -c initials_only=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp_no_planning/bombProblems/instances/btc/btc_bomb_0${i}.sh
    chmod -x benchmarks/ep_asp/bombProblems/instances/btc/btc_bomb_0${i}.sh
    chmod -x benchmarks/ep_asp_no_planning/bombProblems/instances/btc/btc_bomb_0${i}.sh
    echo "Done btc ${i}"

    echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/btuc_conf.lp -c np=$np_len -c len=1 -c length=${i} -c planning=1 -c heuristic=1 -c debug=0 -c initials_only=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp/bombProblems/instances/btuc/btuc_bomb_0${i}.sh
    echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/btuc_conf_np.lp -c np=$np_len -c len=1 -c length=${i} -c planning=0 -c heuristic=0 -c debug=0 -c initials_only=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp_no_planning/bombProblems/instances/btuc/btuc_bomb_0${i}.sh
    chmod -x benchmarks/ep_asp/bombProblems/instances/btuc/btuc_bomb_0${i}.sh
    chmod -x benchmarks/ep_asp_no_planning/bombProblems/instances/btuc/btuc_bomb_0${i}.sh
    echo "Done btuc ${i}"
done
echo "Instances Bomb Problems Done"

echo "Running Many Bomb Problems"
for i in 10 20 30 40 50 60 70 80 90 100 110 120 130 140 150
do
    np_len=$((i / 2))
    for j in 1 2 3 4
    do    
        echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/bmtc_conf.lp -c np=$np_len -c nt=${j} -c len=1 -c length=${i} -c planning=1 -c heuristic=1 -c debug=0 -c initials_only=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp/bombProblems/many/bmtc/bmtc_bomb_0${i}_0${j}.sh
        echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/bmtc_conf_np.lp -c np=$np_len -c nt=${j} -c len=1 -c length=${i} -c planning=0 -c heuristic=0 -c debug=0 -c initials_only=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp_no_planning/bombProblems/many/bmtc/bmtc_bomb_0${i}_0${j}.sh
        chmod -x benchmarks/ep_asp/bombProblems/many/bmtc/bmtc_bomb_0${i}_0${j}.sh
        chmod -x benchmarks/ep_asp_no_planning/bombProblems/many/bmtc/bmtc_bomb_0${i}_0${j}.sh
        echo "Done many_bmtc ${i}_${j}"

        echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/bmtuc_conf.lp -c np=$np_len -c nt=${j} -c len=1 -c length=${i} -c planning=1 -c heuristic=1 -c debug=0 -c initials_only=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp/bombProblems/many/bmtuc/bmtuc_bomb_0${i}_0${j}.sh
        echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/bmtuc_conf_np.lp -c np=$np_len -c nt=${j} -c len=1 -c length=${i} -c planning=0 -c heuristic=0 -c debug=0 -c initials_only=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp_no_planning/bombProblems/many/bmtuc/bmtuc_bomb_0${i}_0${j}.sh
        chmod -x benchmarks/ep_asp/bombProblems/many/bmtuc/bmtuc_bomb_0${i}_0${j}.sh
        chmod -x benchmarks/ep_asp_no_planning/bombProblems/many/bmtuc/bmtuc_bomb_0${i}_0${j}.sh
        echo "Done many_bmtuc ${i}_${j}"
    done

done
echo "Many Bomb Problems Done"

echo "Running Yale Problems"
echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/yaleProblems/yale1.txt -c len=1 -c length=1 -c planning=1 -c debug=0 -c pre=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp/yaleProblems/yale/yale1.sh
echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/yaleProblems/yale1_np.txt -c len=1 -c length=1 -c planning=0 -c debug=0 -c pre=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp_no_planning/yaleProblems/yale/yale1.sh

echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/yaleProblems/yale2.txt -c len=2 -c length=2 -c planning=1 -c debug=0 -c pre=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp/yaleProblems/yale/yale2.sh
echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/yaleProblems/yale2_np.txt -c len=2 -c length=2 -c planning=0 -c debug=0 -c pre=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp_no_planning/yaleProblems/yale/yale2.sh

echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/yaleProblems/yale3.txt -c len=1 -c length=3 -c planning=1 -c debug=0 -c pre=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp/yaleProblems/yale/yale3.sh
echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/yaleProblems/yale3_np.txt -c len=1 -c length=3 -c planning=0 -c debug=0 -c pre=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp_no_planning/yaleProblems/yale/yale3.sh

echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/yaleProblems/yale4.txt -c len=4 -c length=4 -c planning=1 -c debug=0 -c pre=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp/yaleProblems/yale/yale4.sh
echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/yaleProblems/yale4_np.txt -c len=4 -c length=4 -c planning=0 -c debug=0 -c pre=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp_no_planning/yaleProblems/yale/yale4.sh

echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/yaleProblems/yale5.txt -c len=4 -c length=5 -c planning=1 -c debug=0 -c pre=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp/yaleProblems/yale/yale5.sh
echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/yaleProblems/yale5_np.txt -c len=4 -c length=5 -c planning=0 -c debug=0 -c pre=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp_no_planning/yaleProblems/yale/yale5.sh

# echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/yaleProblems/yale6_7.txt -c len=4 -c length=6 -c planning=1 -c debug=0 -c pre=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp/yaleProblems/yale/yale6.sh
# echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/yaleProblems/yale6_7_np.txt -c len=4 -c length=6 -c planning=0 -c debug=0 -c pre=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp_no_planning/yaleProblems/yale/yale6.sh

echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/yaleProblems/yale6_7.txt -c len=4 -c length=7 -c planning=1 -c debug=0 -c pre=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp/yaleProblems/yale/yale7.sh
echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/yaleProblems/yale6_7_np.txt -c len=4 -c length=7 -c planning=0 -c debug=0 -c pre=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp_no_planning/yaleProblems/yale/yale7.sh

echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/yaleProblems/yale8.txt -c len=8 -c length=8 -c planning=1 -c debug=0 -c pre=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp/yaleProblems/yale/yale8.sh
echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/yaleProblems/yale8_np.txt -c len=8 -c length=8 -c planning=0 -c debug=0 -c pre=0 -c max=0 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp_no_planning/yaleProblems/yale/yale8.sh

echo "Yale Problems Done"

echo "Running Instances Eligible Problems"
for i in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25
do
    echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/eligible/eligible${i}.elps.elp -c pre=1 -c max=1 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp/eligible/eligible${i}.sh
    echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/eligible/eligible${i}.elps.elp -c pre=1 -c max=1 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp_no_planning/eligible/eligible${i}.sh
    echo "Done eligible${i}"

done
echo "Finish Eligible instances script creation"

echo "Running new-Eligible Instances"
# Define the directory for new-Eligible
DIR="${current_dir}/benchmarks/new_eligible"

# Extract the XXXX numbers from the filenames
numbers=($(ls $DIR | grep -oP 'eligible\K[0-9]{4}(?=-1.lp)'))

# Iterate over the numbers
for number in "${numbers[@]}"; do
    echo "Processing eligible file number: $number"
    echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/new_eligible/eligible$number-1.elps.elp -c pre=1 -c max=1 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp/eligible/eligible$number.sh
    echo "clingo ${current_dir}/benchmark-tool/programs/ep_asp/solver.py ${current_dir}/benchmark-tool/programs/ep_asp/new_eligible/eligible$number-1.elps.elp -c pre=1 -c max=1 -q2 --time-limit=600 --outf=3" > benchmarks/ep_asp_no_planning/eligible/eligible$number.sh
done