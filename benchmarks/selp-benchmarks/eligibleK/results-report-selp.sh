#! /bin/sh

echo "instance;easpGround-time;easp2asp-time;lpopt-time;clingo-time;group-time"
for f in *.elps
do
	for p in selp.easpground selp.easp2asp selp.lpopt selp.clingo selp.groupWorldViews
	do
		grep "time (seconds):" $f.$p.time | cut -d: -f2 | paste -s -d+ | bc
	done \
	| paste -s -d\; | sed -e "s/^/$f\;/g"
done

