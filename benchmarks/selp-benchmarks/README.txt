--- 
    ORIGINAL TEXT. REFER TO NEW UPDATED BENCHMARKS IN PRINCIPAL README.md for how to run this benchmark.
---

This is the collection of benchmark instances, results, and scripts that were used to test selp against EP-ASP. [1]
There are 3 test sets:
* eligibleK: the scholarship eligibility problem. Instances differ in the number of students (1 to 25). Instasnces taken from EP-ASP repository [2]. All instances have a candidate world view, i.e. are consistent.
* simpleYale: the Yale shooting problem where the only fluents are the loadedness of the gun and the liveliness  of the turkey and the only uncertanity is the initial state of the gun (loded or unloaded). Actions are deterministic. Instances differ in the horizon, that is, how long a solution plan has to be (1 to 25). Only instances with horizon >=3 are consistent, i.e. have a conformant plan, i.e. have a candidate world view.
* tree: TreeQBF instances from [3] where the quantifier blocks have been modified to three (e,a,e) of about the same size. They were then translated to ground ELPs by a generalization of the reduction in the hardness proof of Theorem 5 in [4].

--- How to conduct the benchmarks ---

Additionally to what is stated below in the per-testset sections, the following is expected:
* The selp toolbox is expected to reside in tools/selp/ and the 3qbf2easp.py script in tools/3qbf2easp.py. The EP-ASP repository [2] is exprected to be checked out into tools/EP-ASP/.
* Current (Jan 2018) clingo and gringo [7], lpopt [5] and htd_main [6] executables are expected to be found in the $PATH. If they are not in the $PATH, their paths may be specified by special flags to the selp scripts in the *.todo files.
* clingo version 4.5.3 is exprected to have the name clingo4 in the $PATH. Again, otherwise, change the respective calls in the *.todo files.

The *.todo files contain the actual benchmarking. Each line represents one instance-solver pair and when being executed, the respective solver is being timed on the respective instance and files (most notably *.time files) are generated.

-- eligibleK --

Files needed:
* eligibleK/eligibleNN.elps (where NN goes from 01 to 25)
* eligibleK/resuts-report-selp.sh, eligibleK/resuts-report-epasp.sh
* eligibleK.todo

Pre-Computations:
* Convert to EP-ASP internal format: perform
    $> java -jar tools/EP-ASP/elps.jar eligibleK/eligibleNN.elps -o
  for each NN from 01 to 25. This creates eligibleNN.elps.elp files.

Benchmarking:
* run each line in eligibleK.todo

Gathering results:
* cd to eligibleK
* run the results-report-* scripts, which print the timing results in csv format.

-- simpleYale --

Files needed:
* simpleYale/generalYaleN.sp
* simpleYale/resuts-report-selp.sh, simpleYale/resuts-report-epasp.sh
* simpleYale.todo

Pre-Computations:
* create instances with horizon 1 to 25 by substituting each occurrence of 'N' in simpleYale/generalYale.sp with the respective number, creating simpleYale/yaleN.sp for each N from 1 to 25
* Convert to EP-ASP internal format: perform
    $> java -jar tools/EP-ASP/elps.jar simpleYale/yaleN.sp -o
  for each N from 1 to 25. This creates yaleN.sp.elp files.

Benchmarking:
* run each line in simpleYale.todo

Gathering results:
* cd to simpleYale
* run the results-report-* scripts, which print the timing results in csv format.

-- TreeQBF --

Files needed:
* 14 files of style Tree/tree-exa*.qdimacs -- these are QBFs that have been already rewritten to have 3 quantifier blocks
* Tree/results-report-selp.sh, Tree/results-report-epasp.sh
* tree.todo
* tree-generateELP.sh

Pre-Computations:
* translate the QBF instances to ELPs by calling tree-generateELP.sh # this creates files Tree/tree-exa*.qdimacs.easpnot and Tree/tree-exa*.qdimacs.elps
* Convert to EP-ASP internal format: perform
    $> java -jar tools/EP-ASP/elps.jar Tree/tree-exa*.qdimacs.elps -o
  for each *. This creates Tree/tree-exa*.qdimacs.elps.elp files.

Benchmarking:
* run each line in tree.todo

Gathering results:
* cd to Tree
* run the results-report-* scripts, which print the timing results in csv format.



References:
[1] Single-Shot Epistemic Logic Program Solving, Submission #3232 at IJCAI 2018
[2] EP-ASP: https://github.com/tiep/EP-ASP/
[3] TreeQBF instances: http://www.qbflib.org/family_detail.php?idFamily=56
[4] Yi-Dong Shen and Thomas Eiter. Evaluating epistemic negation in answer set programming. Artif. Intell., 237:115–135, 2016.
[5] lpopt version 2.2: www.dbai.tuwien.ac.at/proj/lpopt/
[6] htd_main: https://github.com/mabseher/htd/releases/tag/1.2
[7] clingo, gringo: https://github.com/potassco/clingo/releases/tag/v5.2.2

