This directory contains encodings and instances for the bomb in the toilet problem.

Encodings with the letter ```m``` use instances from the directory ```instances_many``` while the other encodings use instances from the directory ```instances```. Examples

eclingo bt_base.lp bt.lp instances/bom_00010.lp
eclingo bt_base.lp btc.lp instances/bom_00010.lp
eclingo bt_base.lp btuc.lp instances/bom_00010.lp

eclingo bt_base.lp bmtc.lp instances_many/bom_00010.lp
eclingo bt_base.lp bmtuc.lp instances_many/bom_00010.lp


Example USAGE while using the eclingo-benchmark tool:

    eclingo benchmarks/eclingo/bomb_problems/bt_base.lp benchmarks/eclingo/bomb_problems/bt.lp benchmarks/eclingo/bomb_problems/instances/bomb_0001.lp
