import argparse
import os

import benchmark_runner

IDLV = "idlv/idlv"

BENCHMARKS="./benchmarks"
BENCHMARK_TOOL="./benchmark-tool"

# Add command eclingo --ignore-shows --preprocessing-level=3 --no-eclingo-propagate --stats
COMMANDS = {"eclingo": f"eclingo $@\n\n",
            "eclingo-no": f"eclingo --ignore-shows --preprocessing-level=3 --no-eclingo-propagate --stats $@\n\n",
            "ep_asp":  f"bash \"$@\"\n\n",
            "ep_asp_no_planning":  f"bash \"$@\"\n\n",
            "selp":    f"bash \"$@\"\n\n",
            "qasp":    f"bash \"$@\"\n\n"}

SHOW_COMMAND_GROUNDERS = {"show-gringo", "show-idlv"}

COMMAND_GROUNDERS = {"eclingo", "eclingo-no", "ep_asp", "ep_asp_no_planning", "selp", "qasp"}

BENCHMARK_ORIGIN = {}

for command in COMMAND_GROUNDERS:
    BENCHMARK_ORIGIN[command] = BENCHMARKS
    
for command in SHOW_COMMAND_GROUNDERS:
    BENCHMARK_ORIGIN[command] = BENCHMARKS

parser = argparse.ArgumentParser(prog='Run grounder')
subparsers = parser.add_subparsers(title='subcommands', help='additional for help', dest="command")
subparsers.required = True

for command in COMMANDS:
    gringo_parser = subparsers.add_parser(command)
args = parser.parse_args()

command_splitted = args.command.split("-")
if len(command_splitted) > 1 and command_splitted[1] == "forget":
    command_splitted[1] = "pre-forget"
command_dir = "-".join(command_splitted)

# Mirror of benchmark execution for results
BENCHMARK_RUNNING=f"./running/benchmark-tool-{command_dir}"

# -------------------------------------------------------------------------------

def prepare_benchmark_bomb(benchmark_path):
    # Create directory for different set of problems. Encoding Directory
    benchmark_name = os.path.basename(benchmark_path)
    dir = os.path.join(BENCHMARK_RUNNING,"experiments","instances", benchmark_name)
    os.mkdir(dir)
    
    many_dir = os.path.join(dir, "many")
    os.mkdir(many_dir)
    
    base_dir = os.path.join(dir, "base")
    os.mkdir(base_dir)

    # print("\nThe dir: ", dir)
    # print("\nThe dir: ", many_dir)
    # print("\nThe dir: ", base_dir)
    # print()
        
    # For every encoding, run every subset.
    encodings = (encoding for encoding in os.listdir(benchmark_path) if encoding.endswith(".lp")) # encodings
    base_encoding = "./benchmarks/eclingo/bomb_problems/bt_base.lp"
    for encoding in encodings:
        if encoding == "bt_base.lp":
            continue
        else:    
            encoding_path = os.path.join(benchmark_path, os.path.basename(encoding))
            encoding = encoding.split('.')[0]
            
        # print("The encoding path: ", encoding_path)
        # print("The base encoding: ", base_encoding)
        
        instances_path = os.path.join(benchmark_path, "instances")
        # print("The instances path: ", instances_path)
        
        instances_many_path = os.path.join(benchmark_path, "instances_many")
        #print(instances_many_path)
    
        instances = (instance for instance in os.listdir(instances_path) if instance.endswith(".lp")) 
        many_instances = (instance for instance in os.listdir(instances_many_path) if instance.endswith(".lp")) 
        
        if os.path.basename(encoding) == "bmtc" or os.path.basename(encoding) == "bmtuc":
            # Get all instances_many
            
            for many_instance in many_instances:
                instance_many_path = os.path.join(instances_many_path,os.path.basename(many_instance))
                instance = encoding + "_" + many_instance
                
                # Make output paths for every encoding + instance
                output_path = os.path.join(many_dir, os.path.basename(instance)) 
                # print(base_encoding, encoding_path, instance_many_path, output_path) 
                os.system(f"cat {base_encoding} {encoding_path} {instance_many_path} > {output_path}")
        else:
            # Get all instances
            for instance in instances:
                instance_path = os.path.join(instances_path, os.path.basename(instance))
                instance = encoding + "_" + instance            
                
                # Make output paths for every encoding + instance
                output_path = os.path.join(base_dir, os.path.basename(instance))    
                # print(base_encoding, encoding_path, instance_path) 
                os.system(f"cat {base_encoding} {encoding_path} {instance_path} > {output_path}")
                
                
def prepare_benchmark_action(benchmark_path):
    # Create directory for different set of problems. Encoding Directory
    benchmark_name = os.path.basename(benchmark_path)
    dir = os.path.join(BENCHMARK_RUNNING,"experiments","instances", benchmark_name)
    os.mkdir(dir)
    
    encodings = (encoding for encoding in os.listdir(benchmark_path) if encoding.endswith(".eclingo.lp")) # encodings
    for encoding in encodings:
        encoding_path = os.path.join(benchmark_path, os.path.basename(encoding))
        encoding = encoding.split('.')[0]
        # print("The encoding path: ", encoding_path, " on ", encoding)
        
        instances_path = os.path.join(benchmark_path, "instances")
        # print("The instances path: ", instances_path)
        
        instances = (instance for instance in os.listdir(instances_path) if instance.endswith(".lp")) 
        # Get all instances
        for instance in instances:
            instance_path = os.path.join(instances_path, os.path.basename(instance))
            instance = encoding + "_" + instance            
            
            # Make output paths for every encoding + instance
            output_path = os.path.join(dir, os.path.basename(instance))    
            # print(instance_path)
            
            # print(encoding_path, instance_path, output_path)
            os.system(f"cat {encoding_path} {instance_path}  > {output_path}")

def prepare_benchmark_yale(benchmark_path):
    # Create directory for different set of problems. Encoding Directory
    benchmark_name = os.path.basename(benchmark_path)
    dir = os.path.join(BENCHMARK_RUNNING, "experiments", "instances", benchmark_name)
    os.mkdir(dir)
    
    encodings = (encoding for encoding in os.listdir(benchmark_path) if encoding.endswith(".lp")) # encodings
    for encoding in encodings:
        encoding_path = os.path.join(benchmark_path, os.path.basename(encoding))
        encoding = encoding.split('.')[0]
        #print("The encoding path: ", encoding_path, " on ", encoding)
        
        instances_path = os.path.join(benchmark_path, "input")
        # print("The instances path: ", instances_path)
        
        instances = (instance for instance in os.listdir(instances_path) if instance.endswith(".lp")) 
        
        # Get all instances
        for instance in instances:
            instance_path = os.path.join(instances_path, os.path.basename(instance))
            instance = encoding + "_" + instance            
            
            # Make output paths for every encoding + instance
            output_path = os.path.join(dir, os.path.basename(instance))    
            # print("The output path: ", output_path)
            
            # print(encoding_path, instance_path, output_path)
            os.system(f"cat {encoding_path} {instance_path}  > {output_path}")
            
def prepare_benchmark_eligible_eclingo(benchmark_path):
    # Create directory for different set of problems. Encoding Directory
    benchmark_name = os.path.basename(benchmark_path)
    dir = os.path.join(BENCHMARK_RUNNING, "experiments", "instances", benchmark_name)
    os.mkdir(dir)
    
    encodings = (encoding for encoding in os.listdir(benchmark_path) if encoding.endswith(".lp"))
    for encoding in encodings:
        encoding_path = os.path.join(benchmark_path, os.path.basename(encoding))
        encoding = encoding.split('.')[0]
        #print("The encoding path: ", encoding_path, " on ", encoding)
        
        instances_path = os.path.join(benchmark_path, "input")
        instances = (instance for instance in os.listdir(instances_path) if instance.endswith(".lp")) 
        
        # Get all instances
        for instance in instances:
            instance_path = os.path.join(instances_path, os.path.basename(instance))
            instance = encoding + "_" + instance            
            
            # Make output paths for every encoding + instance
            output_path = os.path.join(dir, os.path.basename(instance))    
            # print("The output path: ", output_path)
            
            # print(encoding_path, instance_path, output_path)
            os.system(f"cat {encoding_path} {instance_path}  > {output_path}")

# -------------------------------------------------------------------------------

def prepare_benchmark_bomb_ep_asp(benchmark_path):
    # Create directory for different set of problems. Encoding Directory
    # print(benchmark_path)
    benchmark_name = os.path.basename(benchmark_path)
    dir = os.path.join(BENCHMARK_RUNNING,"experiments","instances", benchmark_name)
    os.mkdir(dir)
    
    # Get both instances and many subdirs
    directories = os.listdir(benchmark_path)
    for directory in directories:
        
        # Path to the current directory (Instances, many)
        current_dir = os.path.join(benchmark_path, directory)
        
        # Access every different bomb problem set (bt, btc, ...)
        subdirs = os.listdir(current_dir)
        for entry in subdirs:
            
            # Get the full path of the entry
            entry_path = os.path.join(current_dir, entry)
            
            # Check if the entry is a directory
            if os.path.isdir(entry_path):
                for file_name in os.listdir(entry_path):
                    
                    # Move file to experiments
                    file_path = os.path.join(entry_path, file_name)
                    output_path = os.path.join(dir, os.path.basename(file_name))  
                    
                    os.system(f"cat {file_path} > {output_path}")
                    # print(file_path, output_path)

def prepare_benchmark_yale_ep_asp(benchmark_path):
    # Create directory for different set of problems. Encoding Directory
    # print(benchmark_path)
    benchmark_name = os.path.basename(benchmark_path)
    dir = os.path.join(BENCHMARK_RUNNING,"experiments","instances", benchmark_name)
    os.mkdir(dir)
    
    # Get both instances and many subdirs
    directories = os.listdir(benchmark_path)
    for directory in directories:
        
        # Path to the current directory (yale, eiter)
        current_dir = os.path.join(benchmark_path, directory)
        
        # Check if the entry is a directory
        if os.path.isdir(current_dir):
            for file_name in os.listdir(current_dir):
                
                # Move file to experiments
                file_path = os.path.join(current_dir, file_name)
                output_path = os.path.join(dir, os.path.basename(file_name))  
                
                os.system(f"cat {file_path} > {output_path}")

def prepare_benchmark_eligible_ep_asp(benchmark_path):
    benchmark_name = os.path.basename(benchmark_path)
    dir = os.path.join(BENCHMARK_RUNNING,"experiments","instances", benchmark_name)
    os.mkdir(dir)
    
    current_dir = os.path.join(benchmark_path)
    for file_name in os.listdir(current_dir):
        # Move file to experiments
        file_path = os.path.join(current_dir, file_name)
        output_path = os.path.join(dir, os.path.basename(file_name))  
        
        os.system(f"cat {file_path} > {output_path}")

# -------------------------------------------------------------------------------

def prepare_benchmark_eligible_selp(benchmark_path):
    benchmark_name = os.path.basename(benchmark_path)
    dir = os.path.join(BENCHMARK_RUNNING,"experiments","instances", benchmark_name)
    os.mkdir(dir)
    
    current_dir = os.path.join(benchmark_path)
    for file_name in os.listdir(current_dir):
        # Move file to experiments
        file_path = os.path.join(current_dir, file_name)
        output_path = os.path.join(dir, os.path.basename(file_name))  
        
        os.system(f"cat {file_path} > {output_path}")

def prepare_benchmark_yale_selp(benchmark_path):
    benchmark_name = os.path.basename(benchmark_path)
    dir = os.path.join(BENCHMARK_RUNNING,"experiments","instances", benchmark_name)
    os.mkdir(dir)
    
    current_dir = os.path.join(benchmark_path)
    for file_name in os.listdir(current_dir):
        # Move file to experiments
        file_path = os.path.join(current_dir, file_name)
        output_path = os.path.join(dir, os.path.basename(file_name))  
        
        os.system(f"cat {file_path} > {output_path}")
        
def prepare_benchmark_bomb_selp(benchmark_path):
    # Create directory for different set of problems. Encoding Directory
    # print(benchmark_path)
    benchmark_name = os.path.basename(benchmark_path)
    dir = os.path.join(BENCHMARK_RUNNING,"experiments","instances", benchmark_name)
    os.mkdir(dir)
    
    # Get both instances and many subdirs
    directories = os.listdir(benchmark_path)
    for directory in directories:
        
        # Path to the current directory (Instances, many)
        current_dir = os.path.join(benchmark_path, directory)
        
        if os.path.isdir(current_dir):
            # Access every different bomb problem set (bt, btc, ...)
            subdirs = os.listdir(current_dir)
            for entry in subdirs:
                
                # Get the full path of the entry
                entry_path = os.path.join(current_dir, entry)
                
                # Check if the entry is a directory
                if os.path.isdir(entry_path):
                    for file_name in os.listdir(entry_path):
                        
                        # Move file to experiments
                        file_path = os.path.join(entry_path, file_name)
                        output_path = os.path.join(dir, os.path.basename(file_name))  
                        
                        os.system(f"cat {file_path} > {output_path}")
                        
# -------------------------------------------------------------------------------

def prepare_benchmark_bomb_qasp(benchmark_path):
    # Create directory for different set of problems. Encoding Directory
    # print(benchmark_path)
    benchmark_name = os.path.basename(benchmark_path)
    dir = os.path.join(BENCHMARK_RUNNING,"experiments","instances", benchmark_name)
    os.mkdir(dir)
    
    # Get both instances and many subdirs
    directories = os.listdir(benchmark_path)
    for directory in directories:
        
        # Path to the current directory (Instances, many)
        current_dir = os.path.join(benchmark_path, directory)
        
        if os.path.isdir(current_dir):
            # Access every different bomb problem set (bt, btc, ...)
            subdirs = os.listdir(current_dir)
            for entry in subdirs:
                
                # Get the full path of the entry
                entry_path = os.path.join(current_dir, entry)
                
                # Check if the entry is a directory
                if os.path.isdir(entry_path):
                    for file_name in os.listdir(entry_path):
                        
                        # Move file to experiments
                        file_path = os.path.join(entry_path, file_name)
                        output_path = os.path.join(dir, os.path.basename(file_name))  
                        
                        os.system(f"cat {file_path} > {output_path}")
                        
def prepare_benchmark_yale_qasp(benchmark_path):
    benchmark_name = os.path.basename(benchmark_path)
    dir = os.path.join(BENCHMARK_RUNNING,"experiments","instances", benchmark_name)
    os.mkdir(dir)
    
    current_dir = os.path.join(benchmark_path)
    instances = (instance for instance in os.listdir(current_dir) if instance.endswith(".sh")) 
    for file_name in instances:
        # Move file to experiments
        file_path = os.path.join(current_dir, file_name)
        output_path = os.path.join(dir, os.path.basename(file_name))  
        os.system(f"cat {file_path} > {output_path}")
        
def prepare_benchmark_eligible_qasp(benchmark_path):
    benchmark_name = os.path.basename(benchmark_path)
    dir = os.path.join(BENCHMARK_RUNNING,"experiments","instances", benchmark_name)
    os.mkdir(dir)
    
    current_path = os.path.join(benchmark_path)
    instances_path = os.path.join(current_path, "scripts")
    instances = (instance for instance in os.listdir(instances_path) if instance.endswith(".sh")) 
    for file_name in instances:
        # Move file to experiments
        file_path = os.path.join(instances_path, file_name)
        output_path = os.path.join(dir, os.path.basename(file_name))  
        
        os.system(f"cat {file_path} > {output_path}")
    
# -------------------------------------------------------------------------------

def prepare_benchmarks():
    
    # Get specific benchmark origin based on solver used.
    benchmark_origin = BENCHMARK_ORIGIN[args.command]
    
    # Ensure that eclingo-no is redirected to eclingo benchmark folders, but uses extra commands
    benchmark_origin = os.path.join(benchmark_origin, command_dir)
    if benchmark_origin == "./benchmarks/eclingo-no":
        benchmark_origin = "./benchmarks/eclingo"
    
    print(f"benchmark origin: {benchmark_origin}, command dir: {command_dir}")
   
    if command_dir == "eclingo" or command_dir == "eclingo-no":
        print(f"\nUsing solver: Eclingo")
        for benchmark_path in os.listdir(benchmark_origin):
            benchmark_path = os.path.join(benchmark_origin, benchmark_path)
            if os.path.isdir(benchmark_path):

                if os.path.basename(benchmark_path) == "bomb_problems":
                    print("Working on BOMB Problems")
                    prepare_benchmark_bomb(benchmark_path)
                    # pass
                elif os.path.basename(benchmark_path) == "action-reversability":
                    # print("Working on ACTION Problems")
                    # prepare_benchmark_action(benchmark_path)
                    pass
                elif os.path.basename(benchmark_path) == "eligible":
                    print("Working on ELIGIBLE Problems")
                    prepare_benchmark_eligible_eclingo(benchmark_path)
                    # pass
                else:
                    print("Working on YALE Problems")
                    prepare_benchmark_yale(benchmark_path)
                    # pass
                
    elif command_dir == "ep_asp":
        print(f"\nUsing solver: EP-ASP")
        for benchmark_path in os.listdir(benchmark_origin):
            benchmark_path = os.path.join(benchmark_origin, benchmark_path)
            if os.path.isdir(benchmark_path):
                if os.path.basename(benchmark_path) == "bombProblems":
                    print("Working on BOMB Problems")
                    prepare_benchmark_bomb_ep_asp(benchmark_path)
                    # pass
                elif os.path.basename(benchmark_path) == "eligible":
                    print("Working on ELIGIBLE Problems")
                    prepare_benchmark_eligible_ep_asp(benchmark_path)
                    # pass 
                else:
                    print("Working on YALE Problems")
                    prepare_benchmark_yale_ep_asp(benchmark_path)
                    # pass
                
    elif command_dir == "ep_asp_no_planning":
        print(f"\nUsing solver: EP-ASP No Planning")
        for benchmark_path in os.listdir(benchmark_origin):
            benchmark_path = os.path.join(benchmark_origin, benchmark_path)
            if os.path.isdir(benchmark_path):
                if os.path.basename(benchmark_path) == "bombProblems":
                    print("Working on BOMB Problems")
                    prepare_benchmark_bomb_ep_asp(benchmark_path)
                    # pass
                elif os.path.basename(benchmark_path) == "eligible":
                    print("Working on ELIGIBLE Problems")
                    prepare_benchmark_eligible_ep_asp(benchmark_path)
                    # pass
                else:
                    print("Working on YALE Problems")
                    prepare_benchmark_yale_ep_asp(benchmark_path)
                    # pass
                    
    elif command_dir == "selp":
        print(f"\nUsing solver: SELP")
        for benchmark_path in os.listdir(benchmark_origin):
            benchmark_path = os.path.join(benchmark_origin, benchmark_path)
            if os.path.isdir(benchmark_path):
                if os.path.basename(benchmark_path) == "eligibleK":
                    print("Working on ELIGIBLE Problems")
                    prepare_benchmark_eligible_selp(benchmark_path)
                    # pass
                elif os.path.basename(benchmark_path) == "bomb_problems":
                    print("Working on BOMB Problems")
                    prepare_benchmark_bomb_selp(benchmark_path)
                    # pass
                else:
                    print("Working on YALE Problems")
                    prepare_benchmark_yale_selp(benchmark_path)
                    # pass
                    
    elif command_dir == "qasp":
        print(f"\nUsing solver: QASP")
        for benchmark_path in os.listdir(benchmark_origin):
            benchmark_path = os.path.join(benchmark_origin, benchmark_path)
            if os.path.isdir(benchmark_path):
                if os.path.basename(benchmark_path) == "bomb_problems":
                    print("Working on BOMB Problems")
                    prepare_benchmark_bomb_qasp(benchmark_path)
                    # pass
                elif os.path.basename(benchmark_path) == "eligible":
                    print("Working on ELIGIBLE Problems")
                    prepare_benchmark_eligible_qasp(benchmark_path)
                    # pass
                else:
                    print("Working on YALE Problems")
                    prepare_benchmark_yale_qasp(benchmark_path)
                    # pass
                
                
def grounder_solver(solver_file):
    solver_file.write("#!/bin/bash\n")
    solver_file.write("#\n")
    solver_file.write(COMMANDS[args.command])

# Declaring config file for instance and benchmark setup
config_file = "run-benchmark.xml"

br = benchmark_runner.BenchmarkRunner(prepare_benchmarks, BENCHMARK_RUNNING, grounder_solver, args.command, config_file)
br.do_benchmarks()