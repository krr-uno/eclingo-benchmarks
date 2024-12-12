import os   
import shutil

BENCHMARK_TOOL="./benchmark-tool"

class BenchmarkRunner():

    def __init__(self, generate_instances, output_directory, solver_generator, name, config=None) -> None:
        self.generate_instances = generate_instances
        self.output_directory = output_directory
        self.solver_generator = solver_generator
        self.config = config
        self.name = name

    def prepare_benchmark_tool(self):
        shutil.rmtree(self.output_directory, ignore_errors=True)
        shutil.copytree(BENCHMARK_TOOL,self.output_directory)
        shutil.rmtree(os.path.join(self.output_directory,"experiments","instances"), ignore_errors=True)
        shutil.rmtree(os.path.join(self.output_directory,"experiments","results"), ignore_errors=True)
        shutil.rmtree(os.path.join(self.output_directory,"output"), ignore_errors=True)
        os.mkdir(os.path.join(self.output_directory,"experiments","instances"))
        solver_path = os.path.join(self.output_directory,"experiments","solver.sh")
        os.remove(solver_path)
        with open(solver_path,'w') as solver_file:
            self.solver_generator(solver_file)
        os.system("chmod +x " + solver_path)
        if self.config:
            print("The run-benchmark.xml file: ", self.config)
            shutil.copyfile(self.config, os.path.join(self.output_directory,"experiments","run-benchmark.xml"))

    def run_benchmarks(self):
        curent_dir = os.getcwd()
        os.chdir(os.path.join(self.output_directory,"experiments"))
        os.system(f"./do_benchmarks.sh {self.name}")
        os.chdir(curent_dir)


    def do_benchmarks(self):
        print("Preparing benchmarks...")
        self.prepare_benchmark_tool()
        self.generate_instances()
        print("Running benchmark...")
        self.run_benchmarks()
        print("Done running benchmark")

# br = BenchmarkRunner(BENCHMARK_TOOL, BENCHMARK_RUNNING, idlv_solver, "idlv")
# br.do_benchmarks()