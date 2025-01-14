"""
This module contains classes that describe a run script.
It can be used to create scripts to start a benchmark
specified by the run script.
"""

__author__ = "Roland Kaminski"

import benchmarktool.tools as tools
import os
from benchmarktool.tools import Sortable, cmp

# needed to embed measurements functions via exec
# pylint: disable-msg=W0611
import benchmarktool.config #@UnusedImport
# pylint: enable-msg=W0611

class Machine(Sortable):
    """
    Describes a machine.
    """
    def __init__(self, name, cpu, memory):
        """
        Initializes a machine.

        Keyword arguments:
        name   - A name uniquely identifying the machine
        cpu    - Some cpu description
        memory - Some memory description
        """
        self.name   = name
        self.cpu    = cpu
        self.memory = memory

    def toXml(self, out, indent):
        """
        Dump the (pretty-printed) XML-representation of the machine.

        Keyword arguments:
        out    - Output stream to write to
        indent - Amount of indentation
        """
        out.write('{1}<machine name="{0.name}" cpu="{0.cpu}" memory="{0.memory}"/>\n'.format(self, indent))

    def __hash__(self):
        """
        Return a hash values using the name of the machine.
        """
        return hash(self.name)

    def __cmp__(self, machine):
        """
        Compare two machines.
        """
        return cmp(self.name, machine.name)

class System(Sortable):
    """
    Describes a system. This includes a solver description
    together with a set of settings.
    """
    def __init__(self, name, version, measures, order):
        """
        Initializes a system. Name and version of the system
        are used to uniquely identify a system.

        Keyword arguments:
        name     - The name of the system
        version  - The version of the system
        measures - A string specifying the measurement function
                   This must be a function given in the config
        order    - An integer used to order different system.
                   This integer should denote the occurrence in
                   the run specification.
        """
        self.name     = name
        self.version  = version
        self.measures = measures
        self.order    = order
        self.settings = {}
        self.config   = None

    def addSetting(self, setting):
        """
        Adds a given setting to the system.
        """
        setting.system = self
        self.settings[setting.name] = setting

    def toXml(self, out, indent, settings = None):
        """
        Dump the (pretty-printed) XML-representation of the system.

        Keyword arguments:
        out     - Output stream to write to
        indent  - Amount of indentation
        setting - If None all the settings of the system are printed,
                  otherwise the given settings are printed
        """
        out.write('{1}<system name="{0.name}" version="{0.version}" measures="{0.measures}" config="{0.config.name}">\n'.format(self, indent))
        if settings == None: settings = self.settings
        for setting in sorted(settings, key=lambda s: s.order):
            setting.toXml(out, indent + "\t")
        out.write('{0}</system>\n'.format(indent))

    def __hash__(self):
        """
        Calculates a hash value for the system using its name and version.
        """
        return hash((self.name, self.version))

    def __cmp__(self, system):
        """
        Compares two systems using name and version.
        """
        return cmp((self.name, self.version), (system.name, system.version))

class Setting(Sortable):
    """
    Describes a setting for a system. This are command line options
    that can be passed to the system. Additionally, settings can be tagged.
    """
    # Javier
    def __init__(self, name, command, options, tag, order, procs, ppn, pbstemplate, attr):
        """
        Initializes a system.

        name        - A name uniquely identifying a setting.
                      (In the scope of a system)
        cmdline     - A string of command line options
        tag         - A set of tags
        order       - An integer specifying the order of settings
                      (This should denote the occurrence in the job specification.
                      Again in the scope of a system.)
        procs       - Number of processes used by the solver (pbs only)
        ppn         - Processes per node (pbs only)
        pbstemplate - Path to pbs-template file (pbs only, related to mpi-version)
        attr        - A dictionary of additional optional attributes.
        """
        self.name        = name
        self.command     = command
        self.options     = options
        self.tag         = tag
        self.order       = order
        self.procs       = procs
        self.ppn         = ppn
        self.pbstemplate = pbstemplate
        self.attr        = attr
    # Javier

    def toXml(self, out, indent):
        """
        Dump a (pretty-printed) XML-representation of the setting.

        Keyword arguments:
        out     - Output stream to write to
        indent  - Amount of indentation
        """
        tag = " ".join(sorted(self.tag))
        out.write('{1}<setting name="{0.name}" command="{0.command}" options="{0.options}" tag="{2}"'.format(self, indent, tag))
        if self.procs != None:
            out.write(' {0}="{1}"'.format("procs", self.procs))
        if self.ppn != None:
            out.write(' {0}="{1}"'.format("ppn", self.ppn))
        if self.pbstemplate != None:
            out.write(' {0}="{1}"'.format("pbstemplate", self.pbstemplate))
        for key, val in self.attr.items():
            out.write(' {0}="{1}"'.format(key, val))
        out.write('/>\n')

    def __hash__(self):
        """
        Calculates a hash value for the setting using its name.
        """
        return hash(self.name)

    def __cmp__(self, setting):
        """
        Compares two settings using their names.
        """
        return cmp(self.name, setting.name)


class Job(Sortable):
    """
    Base class for all jobs.
    """
    # Javier
    def __init__(self, name, timeout, runs, attr, memory=4000):
        """
        Initializes a job.

        Keyword arguments:
        name    - A unique name for a job
        timeout - A timeout in seconds for individual benchmark runs
        runs    - The number of runs per benchmark
        attr    - A dictionary of arbitrary attributes
        """
        self.name    = name
        self.timeout = timeout
        self.memory  = memory
        self.runs    = runs
        self.attr    = attr
    # Javier

    def _toXml(self, out, indent, xmltag, extra):
        """
        Helper function to dump a (pretty-printed) XML-representation of a job.

        Keyword arguments:
        out     - Output stream to write to
        indent  - Amount of indentation
        xmltag  - Tag name for the job
        extra   - Additional arguments for the job
        """
        out.write('{1}<{2} name="{0.name}" timeout="{0.timeout}" runs="{0.runs}"{3}'.format(self, indent, xmltag, extra))
        for key, val in self.attr.items():
            out.write(' {0}="{1}"'.format(key, val))
        out.write('/>\n')

    def __hash__(self):
        """
        Calculates a hash value for the job using its name.
        """
        return hash(self.name)

    def __cmp__(self, job):
        """
        Compares two jobs using their names.
        """
        return cmp(job.name, job.name)

class Run(Sortable):
    """
    Base class for all runs.

    Class members:
    path - Path that holds the target location for start scripts
    root - directory relative to the location of the run's path.
    """
    def __init__(self, path):
        """
        Initializes a run.

        Keyword arguments:
        path - A path that holds the location
               where the individual start scripts for the job shall be generated
        """
        self.path = path
        self.root = os.path.relpath(".", self.path)

class SeqRun(Run):
    """
    Describes a sequential run.

    Class members:
    run      - The number of the run
    job      - A reference to the job description
    runspec  - A reference to the run description
    instance - A reference to the instance to benchmark
    file     - A relative path to the instance
    args     - The command line arguments for this run
    solver   - The solver for this run
    timeout  - The timeout of this run
    """
    def __init__(self, path, run, job, runspec, instance):
        """
        Initializes a sequential run.

        Keyword arguments:
        path     - A path that holds the location
                   where the individual start scripts for the job shall be generated
        run      - The number of the run
        job      - A reference to the job description
        runspec  - A reference to the run description
        instance - A reference to the instance to benchmark
        """
        Run.__init__(self, path)
        self.run      = run
        self.job      = job
        self.runspec  = runspec
        self.instance = instance
        self.file     = os.path.relpath(self.instance.path(), self.path)
        self.command  = self.runspec.setting.command
        self.options  = self.runspec.setting.options
        self.solver   = self.runspec.system.name + "-" + self.runspec.system.version
        self.timeout  = self.job.timeout
        # Javier
        self.memory   = self.job.memory
        # Javier

class ScriptGen:
    """
    A class providing basic functionality to generate
    start scripts for arbitrary jobs and evaluation of results.
    """
    def __init__(self, job):
        """
        Initializes the script generator.

        Keyword arguments:
        seqJob - A reference to the associated job.
        """
        self.job        = job
        self.startfiles = []

    def _path(self, runspec, instance, run):
        """
        Returns the relative path to the start script location.

        Keyword arguments:
        runspec  - The run specification for the start script
        instance - The benchmark instance for the start script
        run      - The number of the run for the start script
        """
        return os.path.join(runspec.path(), instance.classname.name, instance.instance, "run%d" % run)

    def addToScript(self, runspec, instance):
        """
        Creates a new start script for the given instance.

        Keyword arguments:
        runspec  - The run specification for the start script
        instance - The benchmark instance for the start script
        """
        for run in range(1, self.job.runs + 1):
            path = self._path(runspec, instance, run)
            tools.mkdir_p(path)
            startpath = os.path.join(path, "start.sh")
            template  = open(runspec.system.config.template).read()
            startfile = open(startpath, "w")
            startfile.write(template.format(run=SeqRun(path, run, self.job, runspec, instance)))
            startfile.close()
            self.startfiles.append((runspec, path, "start.sh"))
            tools.setExecutable(startpath)

    def evalResults(self, out, indent, runspec, instance):
        """
        Parses the results of a given benchmark instance and outputs them as XML.

        Keyword arguments:
        out     - Output stream to write to
        indent  - Amount of indentation
        runspec - The run specification of the benchmark
        runspec - The benchmark instance
        """
        for run in range(1, self.job.runs + 1):
            out.write('{0}<run number="{1}">\n'.format(indent, run))
            result = getattr(benchmarktool.config, runspec.system.measures)(self._path(runspec, instance, run), runspec, instance)
            for key, valtype, val in sorted(result):
                out.write('{0}<measure name="{1}" type="{2}" val="{3}"/>\n'.format(indent + "\t", key, valtype, val))
            out.write('{0}</run>\n'.format(indent))

class SeqScriptGen(ScriptGen):
    """
    A class that generates and evaluates start scripts for sequential runs.
    """
    def __init__(self, seqJob):
        """
        Initializes the script generator.

        Keyword arguments:
        seqJob - A reference to the associated sequential job.
        """
        ScriptGen.__init__(self, seqJob)

    def genStartScript(self, path):
        """
        Generates a start script that can be used to start all scripts
        generated using addToScript().

        Keyword arguments:
        path - The target location for the script
        """
        tools.mkdir_p(path)
        startfile = open(os.path.join(path, "start.py"), 'w')
        queue = ""
        comma = False
        # print(self.startfiles)
        for (_, instpath, instname) in self.startfiles:
            relpath = os.path.relpath(instpath, path)
            if comma: queue += ","
            else: comma  = True
            queue+= repr(os.path.join(relpath, instname))
        startfile.write("""\
#!/usr/bin/python -u

import optparse
import threading
import subprocess
import os
import sys
import signal
import time

queue = [{0}]

class Main:
    def __init__(self):
        self.running  = set()
        self.cores    = set()
        self.started  = 0
        self.total    = None
        self.finished = threading.Condition()
        self.coreLock = threading.Lock()
        c = 0
        while len(self.cores) < {1}:
            self.cores.add(c)
            c += 1

    def finish(self, thread):
        self.finished.acquire()
        self.running.remove(thread)
        with self.coreLock:
            self.cores.add(thread.core)
        self.finished.notify()
        self.finished.release()

    def start(self, cmd):
        core     = 0
        with self.coreLock:
            core = self.cores.pop()
        thread = Run(cmd, self, core)
        self.started += 1
        self.running.add(thread)
        print("({{0}}/{{1}}/{{2}}/{{4}}) {{3}}".format(len(self.running), self.started, self.total, cmd, core))
        thread.start()

    def run(self, queue):
        signal.signal(signal.SIGTERM, self.exit)
        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        self.finished.acquire()
        self.total = len(queue)
        for cmd in queue:
            while len(self.running) >= {1}:
                self.finished.wait()
            self.start(cmd)
        while len(self.running) != 0:
            self.finished.wait()
        self.finished.release()

    def exit(self, *args):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        print "WARNING: it is not guaranteed that all processes will be terminated!"
        print "sending sigterm ..."
        os.killpg(os.getpgid(0), signal.SIGTERM)
        print "waiting 10s..."
        time.sleep(10)
        print "sending sigkill ..."
        os.killpg(os.getpgid(0), signal.SIGKILL)

class Run(threading.Thread):
    def __init__(self, cmd, main, core):
        threading.Thread.__init__(self)
        self.cmd  = cmd
        self.main = main
        self.core = core
        self.proc = None

    def run(self):
        path, script = os.path.split(self.cmd)
        self.proc = subprocess.Popen(["bash", script, str(self.core)], cwd=path)
        self.proc.wait()
        self.main.finish(self)

def gui():
    import Tkinter
    class App:
        def __init__(self):
            root    = Tkinter.Tk()
            frame   = Tkinter.Frame(root)
            scrollx = Tkinter.Scrollbar(frame, orient=Tkinter.HORIZONTAL)
            scrolly = Tkinter.Scrollbar(frame)
            list    = Tkinter.Listbox(frame, selectmode=Tkinter.MULTIPLE)

            for script in queue:
                list.insert(Tkinter.END, script)

            scrolly.config(command=list.yview)
            scrollx.config(command=list.xview)
            list.config(yscrollcommand=scrolly.set)
            list.config(xscrollcommand=scrollx.set)

            scrolly.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
            scrollx.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
            list.pack(fill=Tkinter.BOTH, expand=1)

            button = Tkinter.Button(root, text='Run', command=self.pressed)

            frame.pack(fill=Tkinter.BOTH, expand=1)
            button.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)

            self.root  = root
            self.list  = list
            self.run   = False
            self.queue = []

        def pressed(self):
            sel = self.list.curselection()
            for index in sel:
                global queue
                self.queue.append(queue[int(index)])
            self.root.destroy()

        def start(self):
            self.root.mainloop()
            return self.queue

    global queue
    queue.sort()
    queue = App().start()

if __name__ == '__main__':
    usage  = "usage: %prog [options] <runscript>"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-g", "--gui", action="store_true", dest="gui", default=False, help="start gui to selectively start benchmarks")

    opts, args = parser.parse_args(sys.argv[1:])
    if len(args) > 0: parser.error("no arguments expected")

    os.chdir(os.path.dirname(sys.argv[0]))
    if opts.gui: gui()

    m = Main()
    m.run(queue)
""".format(queue, self.job.parallel))
        startfile.close()
        tools.setExecutable(os.path.join(path, "start.py"))

class PbsScriptGen(ScriptGen):
    """
    A class that generates and evaluates start scripts for pbs runs.
    """
    class PbsScript:
        def __init__(self, runspec, path, queue):
            self.runspec      = runspec
            self.path         = path
            self.queue        = queue
            self.num          = 0
            self.time         = None
            self.startscripts = None
            self.next()

        def write(self):
            if self.num > 0:
                self.num = 0
                template = open(self.runspec[2], "r").read()
                script   = os.path.join(self.path, "start{0:04}.pbs".format(len(self.queue)))
                open(script, "w").write(template.format(walltime=tools.pbsTime(self.runspec[3]), nodes=self.runspec[1], ppn=self.runspec[0], jobs=self.startscripts, cpt=self.runspec[4], partition=self.runspec[5]))
                self.queue.append(script)

        def next(self):
            self.write()
            self.startscripts = ""
            self.num          = 0
            self.time         = 0

        def append(self, startfile):
            self.num          += 1
            self.startscripts += startfile + "\n"

    def __init__(self, seqJob):
        """
        Initializes the script generator.

        Keyword arguments:
        seqJob - A reference to the associated sequential job.
        """
        ScriptGen.__init__(self, seqJob)

    def genStartScript(self, path):
        """
        Generates a start script that can be used to start all scripts
        generated using addToScript().

        Keyword arguments:
        path - The target location for the script
        """
        tools.mkdir_p(path)
        startfile = open(os.path.join(path, "start.sh"), 'w')
        queue      = []
        pbsScripts = {}
        for (runspec, instpath, instname) in self.startfiles:
            relpath   = os.path.relpath(instpath, path)
            jobScript = os.path.join(relpath, instname)
            pbsKey    = (runspec.setting.ppn, runspec.setting.procs, runspec.setting.pbstemplate, runspec.project.job.walltime, runspec.project.job.cpt, runspec.project.job.partition)

            if not pbsKey in pbsScripts:
                pbsScript = PbsScriptGen.PbsScript(pbsKey, path, queue)
                pbsScripts[pbsKey] = pbsScript
            else: pbsScript = pbsScripts[pbsKey]

            if self.job.script_mode == "multi":
                if pbsScript.num > 0: pbsScript.next()
                pbsScript.append(jobScript)
            elif self.job.script_mode == "timeout":
                if pbsScript.time + runspec.project.job.timeout + 300 >= runspec.project.job.walltime:
                    pbsScript.next()
                pbsScript.time += runspec.project.job.timeout + 300
                pbsScript.append(jobScript)

        for pbsScript in pbsScripts.values(): pbsScript.write()

        startfile.write("""#!/bin/bash\n\ncd "$(dirname $0)"\n""" + "\n".join(['sbatch "{0}"'.format(os.path.basename(x)) for x in queue]))
        startfile.close()
        tools.setExecutable(os.path.join(path, "start.sh"))

class SeqJob(Job):
    """
    Describes a sequential job.
    """
    # Javier
    def __init__(self, name, timeout, runs, parallel, attr, memory):
        """
        Initializes a sequential job description.

        Keyword arguments:
        name     - A unique name for a job
        timeout  - A timeout in seconds for individual benchmark runs
        runs     - The number of runs per benchmark
        parallel - The number of runs that can be started in parallel
        attr     - A dictionary of arbitrary attributes
        """
        Job.__init__(self, name, timeout, runs, attr, memory)
        self.parallel = parallel
    # Javier

    def scriptGen(self):
        """
        Returns a class that can generate start scripts and evaluate benchmark results.
        (see SeqScriptGen)
        """
        return SeqScriptGen(self)

    def toXml(self, out, indent):
        """
        Dump a (pretty-printed) XML-representation of the sequential job.

        Keyword arguments:
        out     - Output stream to write to
        indent  - Amount of indentation
        """
        extra = ' parallel="{0.parallel}"'.format(self)
        Job._toXml(self, out, indent, "seqjob", extra)


class PbsJob(Job):
    """
    Describes a pbs job.
    """
    def __init__(self, name, timeout, runs, script_mode, walltime, cpt, memory, partition, attr):
        """
        Initializes a parallel job description.

        Keyword arguments:
        name        - A unique name for a job
        timeout     - A timeout in seconds for individual benchmark runs
        runs        - The number of runs per benchmark
        script_mode - Specifies the script generation mode
        walltime    - The walltime for a job submitted via PBS
        cpt         - Number of cpus per tasks for SLURM # Javier
        memory      - Maximum memory allowed # Javier
        partition   - Partition to be used in the cluster (kr by default) # Javier
        attr        - A dictionary of arbitrary attributes
        """
        Job.__init__(self, name, timeout, runs, attr)
        self.script_mode = script_mode
        self.walltime    = walltime
        self.cpt         = cpt # Javier
        self.memory      = memory # Javier
        self.partition   = partition # Javier

    def toXml(self, out, indent):
        """
        Dump a (pretty-printed) XML-representation of the parallel job.

        Keyword arguments:
        out     - Output stream to write to
        indent  - Amount of indentation
        """
        extra = ' script_mode="{0.script_mode}" walltime="{0.walltime}" cpt="{0.cpt}" memory="{0.memory}" partition="{0.partition}"'.format(self)
        Job._toXml(self, out, indent, "pbsjob", extra)

    def scriptGen(self):
        """
        Returns a class that can generate start scripts and evaluate benchmark results.
        (see SeqScriptGen)
        """
        return PbsScriptGen(self)

class Config(Sortable):
    """
    Describes a configuration. Currently, this only specifies a template
    that is used for start script generation.
    """
    def __init__(self, name, template):
        """
        Keyword arguments:
        name     - A name uniquely identifying the configuration
        template - A path to the template for start script generation
        """
        self.name     = name
        self.template = template

    def toXml(self, out, indent):
        """
        Dump a (pretty-printed) XML-representation of the configuration.

        Keyword arguments:
        out     - Output stream to write to
        indent  - Amount of indentation
        """
        out.write('{1}<config name="{0.name}" template="{0.template}"/>\n'.format(self, indent))

    def __hash__(self):
        """
        Calculates a hash value for the configuration using its name.
        """
        return hash(self.name)

    def __cmp__(self, config):
        """
        Compares two configurations using their names.
        """
        return cmp(config.name, config.name)

class Benchmark(Sortable):
    """
    Describes a benchmark. This includes a set of classes
    that describe where to find particular instances.
    """
    class Class(Sortable):
        """
        Describes a benchmark class.
        """
        def __init__(self, name):
            """
            Initializes a benchmark class.

            Keyword arguments:
            name - A name uniquely identifying a benchmark class (per benchmark).
            """
            self.name = name
            self.id   = None

        def __cmp__(self, other):
            """
            Compares two benchmark classes using their names.
            """
            return cmp(self.name, other.name)

        def __hash__(self):
            """
            Calculates a hash value for the benchmark class using its name.
            """
            return hash(self.name)

    class Instance(Sortable):
        """
        Describes a benchmark instance.
        """
        def __init__(self, location, classname, instance):
            """
            Initializes a benchmark instance. The instance name uniquely identifies
            an instance (per benchmark class).

            Keyword arguments:
            location  - The location of the benchmark instance.
            classname - The class name of the instance
            instance  - The name of the instance
            """
            self.location  = location
            self.classname = classname
            self.instance  = instance
            self.id        = None

        def toXml(self, out, indent):
            """
            Dump a (pretty-printed) XML-representation of the configuration.

            Keyword arguments:
            out     - Output stream to write to
            indent  - Amount of indentation
            """
            out.write('{1}<instance name="{0.instance}" id="{0.id}"/>\n'.format(self, indent))

        def __cmp__(self, instance):
            """
            Compares tow instances using the instance name.
            """
            return cmp(self.instance, instance.instance)

        def __hash__(self):
            """
            Calculates a hash using the instance name.
            """
            return hash(self.instance)

        def path(self):
            """
            Returns the location of the instance by concatenating
            location, class name and instance name.
            """
            return os.path.join(self.location, self.classname.name, self.instance)

    class Folder:
        """
        Describes a folder that should recursively be scanned for benchmarks.
        """
        def __init__(self, path):
            """
            Initializes a benchmark folder.

            Keyword arguments:
            path - The location of the folder
            """
            self.path     = path
            self.prefixes = set()
            self.dir_ignore_prefixes  = set()
            self.dir_accept_prefixes  = set()
            self.file_ignore_prefixes = set()
            self.file_accept_prefixes = set()

        def addIgnore(self, prefix):
            """
            Can be used to ignore certain sub-folders or instances
            by giving a path prefix that shall be ignored.

            Keyword arguments:
            prefix - The prefix to be ignored
            """
            self.prefixes.add(os.path.normpath(prefix))

        # Javier

        def addDirIgnore(self, prefix):
            self.dir_ignore_prefixes.add(prefix)

        def addDirAccept(self, prefix):
            self.dir_accept_prefixes.add(prefix)

        def addFileIgnore(self, prefix):
            self.file_ignore_prefixes.add(prefix)

        def addFileAccept(self, prefix):
            self.file_accept_prefixes.add(prefix)

        # Javier

        def _skip_dir(self, root, path):
            """
            Returns whether a given directory path should be ignored.

            Keyword arguments:
            root - The root path
            path - Some path relative to the root path
            """
            if path == ".svn": return True
            bigpath = os.path.normpath(os.path.join(root, path))
            if bigpath in self.prefixes:            return True
            for i in self.dir_ignore_prefixes:
                if path.startswith(i): return True
            if len(self.dir_accept_prefixes)>0:
                for i in dir.file_accept_prefixes:
                    if path.startswith(i): return False
                return True
            return False
            #return path in self.prefixes

        def _skip_file(self, root, path):
            for i in self.file_ignore_prefixes:
                if path.startswith(i): return True
            if len(self.file_accept_prefixes)>0:
                for i in self.file_accept_prefixes:
                    if path.startswith(i): return False
                return True
            return False

        def init(self, benchmark):
            """
            Recursively scans the folder and adds all instances found to the given benchmark.

            Keyword arguments:
            benchmark - The benchmark to be populated.
            """
            for root, dirs, files in os.walk(self.path):
                relroot = os.path.relpath(root, self.path)
                sub = []
                for dirname in dirs:
                    if self._skip_dir(relroot, dirname): continue
                    sub.append(dirname)
                dirs[:] = sub
                for filename in files:
                    if self._skip_file(relroot, filename): continue
                    benchmark.addInstance(self.path, relroot, filename)
        # Javier


    class Files:
        """
        Describes a set of individual files in a benchmark.
        """
        def __init__(self, path):
            """
            Initializes to the empty set of files.

            Keyword arguments:
            path - Root path, all file paths are relative to this path
            """
            self.path  = path
            self.files = set()

        def addFile(self, path):
            """
            Adds a file to the set of files.

            Keyword arguments:
            path - Location of the file
            """
            self.files.add(os.path.normpath(path))

        def init(self, benchmark):
            """
            Adds a files in the set to the given benchmark (if they exist).

            Keyword arguments:
            benchmark - The benchmark to be populated
            """
            for path in self.files:
                if os.path.exists(os.path.join(self.path, path)):
                    relroot, filename = os.path.split(path)
                    benchmark.addInstance(self.path, relroot, filename)

    def __init__(self, name):
        """
        Initializes an empty benchmark set.

        Keyword arguments:
        name - The name of the benchmark set
        """
        self.name        = name
        self.elements    = []
        self.instances   = {}
        self.initialized = False

    def addElement(self, element):
        """
        Adds elements to the benchmark, e.g, files or folders.

        Keyword arguments:
        element - The element to add
        """
        self.elements.append(element)

    def addInstance(self, root, relroot, filename):
        """
        Adds an instance to the benchmark set. (This function
        is called during initialization by the benchmark elements)

        Keyword arguments:
        root     - The root folder of the instance
        relroot  - The folder relative to the root folder
        filename - The filename of the instance
        """
        classname = Benchmark.Class(relroot)
        if not classname in self.instances:
            self.instances[classname] = set()
        self.instances[classname].add(Benchmark.Instance(root, classname, filename))

    def init(self):
        """
        Populates the benchmark set with instances specified by the
        benchmark elements added.
        """
        if not self.initialized:
            for element in self.elements: element.init(self)
            classid = 0
            for classname in sorted(self.instances.keys()):
                classname.id = classid
                classid += 1
                instanceid = 0
                for instance in sorted(self.instances[classname]):
                    instance.id = instanceid
                    instanceid += 1
            self.initialized = True


    def toXml(self, out, indent):
        """
        Dump the (pretty-printed) XML-representation of the benchmark set.

        Keyword arguments:
        out    - Output stream to write to
        indent - Amount of indentation
        """
        self.init()
        out.write('{1}<benchmark name="{0}">\n'.format(self.name, indent))
        for classname in sorted(self.instances.keys()):
            instances = self.instances[classname]
            out.write('{1}<class name="{0.name}" id="{0.id}">\n'.format(classname, indent + "\t"))
            for instance in sorted(instances):
                instance.toXml(out, indent + "\t\t")
            out.write('{0}</class>\n'.format(indent + "\t"))
        out.write('{0}</benchmark>\n'.format(indent))

    def __hash__(self):
        """
        Return a hash values using the name of the machine.
        """
        return hash(self.name)

    def __cmp__(self, benchmark):
        """
        Compare two benchmark sets.
        """
        return cmp(benchmark.name, benchmark.name)

class Runspec(Sortable):
    """
    Describes a run specification. This specifies system, settings, machine
    to run a benchmark with.
    """
    def __init__(self, machine, setting, benchmark):
        """
        Initializes a run specification.

        Keyword arguments:
        machine   - The machine to run on
        setting   - The setting to run with (includes system)
        benchmark - The benchmark
        """
        self.machine   = machine
        self.setting   = setting
        self.system    = setting.system
        self.benchmark = benchmark
        self.project   = None

    def path(self):
        """
        Returns an output path under which start scripts
        and benchmark results are stored.
        """
        name = self.setting.system.name + "-" + self.setting.system.version + "-" + self.setting.name
        return os.path.join(self.project.path(), self.machine.name, "results", self.benchmark.name, name)

    def genScripts(self, scriptGen):
        """
        Generates start scripts needed to start the benchmark described
        by this run specification. This will simply add all instances
        to the given script generator.

        Keyword arguments:
        scriptGen - A generator that is responsible for the start script generation
        """
        self.benchmark.init()
        for instances in self.benchmark.instances.values():
            for instance in instances:
                scriptGen.addToScript(self, instance)

    def __cmp__(self, runspec):
        """
        Compares two run specifications.
        """
        return cmp((self.machine, self.system, self.setting, self.benchmark), (runspec.machine, runspec.system, runspec.setting, runspec.benchmark))

class Project(Sortable):
    """
    Describes a benchmark project, i.e., a set of run specifications
    that belong together.
    """
    def __init__(self, name):
        """
        Initializes an empty project.

        Keyword arguments:
        name - The name of the project
        """
        self.name      = name
        self.runspecs  = {}
        self.runscript = None
        self.job       = None

    def addRuntag(self, machine, benchmark, tag):
        """
        Adds a run tag to the project, i.e., a set of run specifications
        identified by certain tags.

        Keyword arguments:
        machine   - The machine to run on
        benchmark - The benchmark set to evaluate
        tag       - The tags of systems+settings to run
        """
        disj = TagDisj(tag)
        for system in self.runscript.systems.values():
            for setting in system.settings.values():
                if disj.match(setting.tag):
                    self.addRunspec(machine, system.name, system.version, setting.name, benchmark)

    def addRunspec(self, machine, system, version, setting, benchmark):
        """
        Adds a run specification, described by machine, system+settings, and benchmark set,
        to the project.

        Keyword arguments:
        machine   - The machine to run on
        system    - The system to evaluate
        version   - The version of the system
        setting   - The settings to run the system with
        benchmark - The benchmark set to evaluate
        """
        runspec = Runspec(self.runscript.machines[machine],
                          self.runscript.systems[(system,version)].settings[setting],
                          self.runscript.benchmarks[benchmark])
        runspec.project = self
        if not machine in self.runspecs: self.runspecs[machine] = []
        self.runspecs[machine].append(runspec)

    def path(self):
        """
        Returns an output path under which start scripts
        and benchmark results are stored for this project.
        """
        return os.path.join(self.runscript.path(), self.name)

    def genScripts(self):
        """
        Generates start scripts for this project.
        """
        for machine, runspecs in self.runspecs.items():
            scriptGen = self.job.scriptGen()
            for runspec in runspecs:
                runspec.genScripts(scriptGen)
            scriptGen.genStartScript(os.path.join(self.path(), machine))

    def __hash__(self):
        """
        Return a hash values using the name of the project.
        """
        return hash(self.name)

    def __cmp__(self, project):
        """
        Compares two projects.
        """
        return cmp(project.name, project.name)

class Runscript:
    """
    Describes a run script, i.e., everything that is needed
    to start and evaluate a set of benchmarks.
    """
    def __init__(self, output):
        """
        Initializes an empty run script.

        Keyword arguments:
        output - The output folder to store start scripts and result files
        """
        self.output     = output
        self.jobs       = {}
        self.projects   = {}
        self.machines   = {}
        self.systems    = {}
        self.configs    = {}
        self.benchmarks = {}

    def addMachine(self, machine):
        """
        Adds a given machine to the run script.
        """
        self.machines[machine.name] = machine

    def addSystem(self, system, config):
        """
        Adds a given system to the run script.
        Additionally, each system will be associated with a config.

        Keyword arguments:
        system - The system to add
        config - The name of the config of the system
        """
        system.config = self.configs[config]
        self.systems[(system.name, system.version)] = system

    def addConfig(self, config):
        """
        Adds a configuration to the run script.
        """
        self.configs[config.name] = config

    def addBenchmark(self, benchmark):
        """
        Adds a benchmark to the run script.
        """
        self.benchmarks[benchmark.name] = benchmark

    def addJob(self, job):
        """
        Adds a job to the runscript.
        """
        self.jobs[job.name] = job

    def addProject(self, project, job):
        """
        Adds a project to therun script.
        Additionally, the project ill be associated with a job.

        Keyword arguments:
        project - The project to add
        job     - The name of the job of the project
        """
        project.runscript = self
        project.job       = self.jobs[job]
        self.projects[project.name] = project

    def genScripts(self):
        """
        Generates the start scripts for all benchmarks described by
        this run script.
        """
        for project in self.projects.values():
            project.genScripts()

    def path(self):
        """
        Returns the output path of this run script.
        """
        return self.output

    def evalResults(self, out):
        """
        Evaluates and prints the results of all benchmarks described
        by this run script. (Start scripts have to be run first.)

        Keyword arguments:
        out - Output stream for xml output
        """
        machines   = set()
        jobs       = set()
        configs    = set()
        systems    = {}
        benchmarks = set()

        for project in self.projects.values():
            jobs.add(project.job)
            for runspecs in project.runspecs.values():
                for runspec in runspecs:
                    machines.add(runspec.machine)
                    configs.add(runspec.system.config)
                    if not runspec.system in systems: systems[runspec.system] = []
                    systems[runspec.system].append(runspec.setting)
                    benchmarks.add(runspec.benchmark)

        out.write('<result>\n')

        for machine in sorted(machines):
            machine.toXml(out, "\t")
        for config in sorted(configs):
            config.toXml(out, "\t")
        for system in sorted(systems.keys(), key=lambda s: s.order):
            system.toXml(out, "\t", systems[system])
        for job in sorted(jobs):
            job.toXml(out, "\t")
        for benchmark in sorted(benchmarks):
            benchmark.toXml(out, "\t")

        for project in self.projects.values():
            out.write('\t<project name="{0.name}" job="{0.job.name}">\n'.format(project))
            jobGen = project.job.scriptGen()
            jobs.add(project.job)
            for runspecs in project.runspecs.values():
                for runspec in runspecs:
                    out.write('\t\t<runspec machine="{0.machine.name}" system="{0.system.name}" version="{0.system.version}" benchmark="{0.benchmark.name}" setting="{0.setting.name}">\n'.format(runspec))
                    for classname in sorted(runspec.benchmark.instances):
                        out.write('\t\t\t<class id="{0.id}">\n'.format(classname))
                        instances =  runspec.benchmark.instances[classname]
                        for instance in instances:
                            out.write('\t\t\t\t<instance id="{0.id}">\n'.format(instance))
                            jobGen.evalResults(out, "\t\t\t\t\t", runspec, instance)
                            out.write('\t\t\t\t</instance>\n')
                        out.write('\t\t\t</class>\n')
                    out.write('\t\t</runspec>\n')
            out.write('\t</project>\n')
        out.write('</result>\n')

class TagDisj:
    """Represents tags in form of a disjunctive normal form."""
    ALL = 1
    def __init__(self, tag):
        """
        Transforms a string into a disjunctive normal form of tags.
        Spaces between tags are interpreted as conjunctions and |
        is interpreted as disjunction. The special value "*all*"
        matches everything.

        Keyword arguments:
        tag -- a string representing a disjunctive normal form of tags
        """
        if tag == "*all*":
            self.tag = self.ALL
        else:
            self.tag = []
            tagDisj = tag.split("|")
            for tagConj in tagDisj:
                tagList = tagConj.split(None)
                self.tag.append(frozenset(tagList))

    def match(self, tag):
        """
        Checks whether a given set of tags is subsumed.

        Keyword arguments:
        tag - a set of tags
        """
        if self.tag == self.ALL:
            return True
        for conj in self.tag:
            if conj.issubset(tag):
                return True
        return False

