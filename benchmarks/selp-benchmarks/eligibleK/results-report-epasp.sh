#! /bin/sh

echo "instance;epasp-time"
for f in *.elps.elp
do
	grep "time (seconds):" $f.epasp.time | cut -d: -f2 | paste -s -d+ | bc | sed -e "s/^/$f\;/g"
done

