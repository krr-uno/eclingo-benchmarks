#!/bin/bash
# reads in EASP-not (possibly with sorts) and outputs the program in EASP-KM (semantically equivalent in EFLP).
sed -re 's/\$not\$/ not K\$ /g' | sed -re 's/not[ \t]+not//g' | sed -re 's/not[ \t]+K\$[ \t]+not/ M\$ /g'

