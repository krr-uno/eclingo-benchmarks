To run the benchmarks and reproduce the results presented in the paper be sure to have read the docummentation:
IMPORTANT TO READ ALL DOCUMENTATIO AND TO FOLLOW ALL THE STEPS.

*Run Benchmarks for different EPISTEMIC SOLVERS*

    
    + Creation of environments step:
        Based on the Epistemic Solver to be run, first create a conda environment executing the respective yml file.

        - EP-ASP or elp2qasp or selp:
            1. Run      -> conda env create -f envs/environment_ep_qasp_selp.yml
            2. Activate -> conda activate ep_qasp_selp

        - Eclingo (original version):
            1. Run      -> conda env create -f envs/environment_eclingo_old.yml
            2. Activate -> conda activate eclingo_old
            3. Install eclingo:
                3.1. Clone the repo into your benchmark directory -> git clone https://github.com/potassco/eclingo.git
                3.2. Install eclingo                              -> cd eclingo/ && pip install .
                    3.2.1. You can check that the correct version of eclingo is installed by running eclingo --version. 
                           It should be eclingo 0.2.0

        - Eclingo (new version):
            1. Run      -> conda env create -f envs/environment_eclingo_reif.yml
            2. Activate -> conda activate eclingo_reif
            3. Install eclingo:
                3.1. Clone the repo into your benchmark directory -> git clone https://github.com/jorgefandinno/eclingo.git
                3.2. Install eclingo                              -> cd eclingo/ && pip install .
                    3.2.1. You can check that the correct version of eclingo is installed by running eclingo --version. 
                           It should be eclingo 0.5.0
        
        + IMPORTANT:
            When installing succesively both eclingo old and eclingo reififcation versions, make sure to change the name of
            the eclingo cloned folder in order to keep both.
            Example: If installed first eclingo old, change the eclingo/ to eclingo_old/ so there are no problems
            when cloning the eclingo/ folder for eclingo reif.
            
    --------------------------------------------------------------------------------------------------------------------------   
    
    + Preparation steps:
        - EP-ASP:
            1. IMPORTANT ON YALE BENCHMARK INSTANCES for ep_asp_no_planning! -> Modify run-benchmark.xml SEQUENTIAL arguments:
                    <seqjob name="seq-generic" runs="1"
                    timeout="610" memory="40000" parallel="4"/>
            
                So memory is increased to solve yale_problem instances memory issues.

            2. Run the script in benchmark-tool/programs/create_scripts/createScriptsEP-ASP.sh
                This will generate the instances of the different benchmarks in the benchmarks/ep_asp folder.
                ep_asp_no_planning option is also generated in that script

        - selp:
            1. Run the script in benchmark-tool/programs/create_scripts/createScriptSelp.sh
                IMPORTANT -> MAKE SURE TO HAVE GRINGO AND CLINGO INSTALLED UNDER YOUR RESPECTIVE CONDA ENVIRONMENT !
                1.1. Change in the script the name of the conda environment if needed. Currently 'ep_asp' as it was 
                the researchers conda environment's name.

            2. benchmark-tool/programs contains different selp related scripts that execute the different instances. Those are:
                - selp (Bomb problems)
                - elp-selp (newEligibleK problems)
                - yale-selp (Yale shooting problems)

        - elp2qasp:

            1. IMPORTANT ON YALE AND BOMB BENCHMARK INSTANCES! -> Modify run-benchmark.xml SEQUENTIAL arguments:
                    <seqjob name="seq-generic" runs="1"
                    timeout="610" memory="40000" parallel="4"/>
            
                So memory is increased to solve yale_problem and bomb_problem instances memory issues.

            2. Run the script in benchmark-tool/programs/create_scripts/createScriptQasp.sh
                - Ensure you have elp-qasp-bomb and elp-qasp in the benchmark-tool/programs directory.
                - These files also have some inner program dependencies.
                    + elp-qasp requires qasp program (also included in benchmark-tool/programs)
                    + elp-qasp-bomb requires qasp.jar (also included in benchmark-tool/programs)
                    + elp-qasp-yale requires qasp.jar (also included in benchmark-tool/programs)


        - eclingo (original and new version):
            No previous step is needed to execute eclingo benchmarks.

        + REQUIREMENT -> Other files required are:
            - easp-km2easp-not.sh
            - easpGrounder.py
            - easp-not2easp-km.sh
            - elp2qasp.py
            - groupWorldViews.py

            These files are required by one or many different epistemic solvers in order to be able to run the benchmarks.
            To reproduce the results just ensure they are part of the benchmark-tool/programs directory.
            
    --------------------------------------------------------------------------------------------------------------------------   

    + Running steps:

        - Execute the benchmarks for a specific epistemic solver:
            1. Run -> nohup ./run.sh {solver_name}
               where {solver_name} is an argument from the list of possible epistemic solvers:
               
                # eclingo               -> Based on the environment used one could run the original version or the new version.
                # eclingo-no            -> Run newer eclingo reification version without propagation of facts.
                # ep_asp                -> Run EP-ASP solver.
                # ep_asp_no_planning    -> Run EP-ASP solver without planning cues given by planning=0 parameter. "Vanilla version".
                # selp                  -> Run selp solver.
                # qasp                  -> Run elp2qasp solver.

               and nohup is a command that prevents the process from stopping even if the computer terminal is closed.

               • TO RUN eclingo-no:
                - On file run-benchmark.xml line 4 to look like:
                    <system name="script" version="0" measures="eclingo" config="generic">
                
                changing 'measures' to eclingo from runsolver will provide solving time that will be used later for plotting.

               • TO RUN eclingo with eclingo_reif conda environment:
                - On file run-benchmark.xml line 4 to look like:
                    <system name="script" version="0" measures="eclingo" config="generic">

                - On file run-benchmark.py, add argument --stats to eclingo execution such as:
                    "eclingo": f"eclingo --stats $@\n\n"

                this will create excel files that are used for the G1 vs G0 figures comparison (eclingo_reif_solving.xlsx) and all solvers comparison (eclingo_reif.xlsx).

                • TO RUN the rest of solvers, make sure to:
                - On file run-benchmark.xml line 4 to look like:
                    <system name="script" version="0" measures="runsolver" config="generic">

            2. In the case that one wants to run a specific benchmark. 
                2.1. Go to run-benchmark.py file.
                2.2. Comment out the specific benchmarks that should not run in the prepare_benchmarks() function.
                2.3. Repeat step 1.

            3. Results will be saved in the running folder under the specific 
            'benchmark-tool-{solver_name}/experiments/results/{solver_name}' folder



    --------------------------------------------------------------------------------------------------------------------------   

    + Data collection steps:

        - To collect the data for the all solvers comparison:
            1. Executing nohup ./run.sh {solver_name} in the step before will automatically generate xlsx files for each solver.
            2. These files will be stored in xperiments/plot directory.
            3. These files will be used to create a .png image similar to the ones used in the paper in the next step.
            * The images will not be 100% similar due to the computer specs used and the stochasticity of the benchmark solver tool *

            • To create or re-generate individual xlsx files you can run:
                python3 xperiments/recreation_excels.py {solver_name}

            with the condition that the 'benchmark-tool-{solver_name}/experiments/results/{solver_name}' folder exists,
            and the instances have been solved previously.

        - AS MENTIONED IN RUNNING STEPS -> To collect the data for the G1 vs G0 solvers:
            1. Important to follow steps previously explained.

            
    + Figure Paper Recreation

        - Once all the other steps have been performed, and there are 6 different xlsx files in the xperiment/plot dir:
            1. Run the file -> python3 xperiments/recreation_plots.py

        - The figures will be shown in the xperiments/plot folder.


Resources
[1] http://www.cs.uni-potsdam.de/clasp
[2] http://www.cril.univ-artois.fr/~roussel/runsolver/
    

