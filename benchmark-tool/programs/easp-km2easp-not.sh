#!/bin/bash
# reads in EASP-KM syntax (possibly with sorts) and outputs the program in EASP-not (semantically equivalent in EFLP)
sed -re 's/K\$/not \$not\$/g' | sed -re 's/M\$/\$not\$ not/g' | sed -re 's/not[ \t]+not//g'

