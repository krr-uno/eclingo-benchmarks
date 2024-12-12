'''
Created on Jan 17, 2010

@author: Roland Kaminski

modified by: Javier
'''

import os
import re
import sys
import codecs

clingo_re = {
    "time"        : ("float",  re.compile(r"^#   total CPU time \(s\): (?P<val>[0-9]+(\.[0-9]+)?)$")),
}

def runsolver(root, runspec, instance):
    """
    Extracts some runsolver statistics.
    """
    timeout = runspec.project.job.timeout
    res     = { "time": ("float", timeout) }
    for f in ["runsolver.solver", "runsolver.watcher", "benchmark.txt"]:
        if f == "benchmark.txt":
            if "choices" in res or not os.path.isfile(os.path.join(root, f)):
                break
            res["status"] = ("string", "UNKNOWN")
        for line in codecs.open(os.path.join(root, f), errors='ignore', encoding='utf-8'):
            for val, reg in clingo_re.items():
                m = reg[1].match(line)
                if m:
                    res[val] = (reg[0], float(m.group("val")) if reg[0] == "float" else m.group("val"))
    # if "memerror" in res or "memerror2" in res:
    #     res["error"]  = ("string", "std::bad_alloc")
    #     res["status"] = ("string", "UNKNOWN")
    #     res.pop("memerror", None)
    #     res.pop("memerror2", None)
    # if "status" in res and res["status"][1] == "OPTIMUM FOUND" and not "optimal" in res:
    #     res["optimal"] = ("float", float("1"))
    result   = []
    # error    = not "status" in res or ("error" in res and res["error"][1] != "std::bad_alloc")
    # memout   = "error" in res and res["error"][1] == "std::bad_alloc"
    # status   = res["status"][1] if "status" in res else None
    # if "models" in res and not "optimal" in res:
    #     res["optimal"] = ("float", float("0"))
    # timedout = memout or error or status == "UNKNOWN" or (status == "SATISFIABLE" and "optimum" in res) or res["time"][1] >= timeout or "interrupted" in res;
    # if timedout: res["time"] = ("float", timeout)
    # if memout:
    #     sys.stderr.write("*** MEMOUT: Run {0} did a memout!\n".format(root))
    # elif error: 
    #     sys.stderr.write("*** ERROR: Run {0} failed with unrecognized status or error!\n".format(root))
    # result.append(("error", "float", int(error)))
    # result.append(("timeout", "float", int(timedout)))
    # result.append(("memout", "float", int(memout)))

    # if "optimum" in res and not " " in res["optimum"][1]:
    #     result.append(("optimum", "float", float(res["optimum"][1])))
    #     del res["optimum"]
    # if "interrupted" in res: del res["interrupted"]
    # if "error" in res: del res["error"]
    for key, val in res.items(): result.append((key, val[0], val[1]))

    # if res["status"][1] == "SATISFIABLE":
    #     is_answer_line = False
    #     for line in codecs.open(os.path.join(root, "runsolver.solver"), errors='ignore', encoding='utf-8'):
    #         if line.startswith("Answer: 1"):
    #             is_answer_line = True
    #             continue
    #         if is_answer_line:
    #             result.append(("answer", "string", line.strip()))
    #             break
    # else:
    #     result.append(("answer", "string", ""))
    return result
