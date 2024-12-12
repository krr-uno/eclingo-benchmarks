
# coding: utf-8

#get_ipython().magic(u'matplotlib notebook')
from cProfile import label
from optparse import Values
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import display, HTML, Markdown, display_jpeg
import re
import math
from pathlib import Path
import itertools



pd.options.display.float_format = '{:,.1f}'.format

class Analyzer:

    def do_get_3df(self, df):

        # Check 
        print(df.isna().all(axis=1)[0])
    
        # Get index of first row will all nan values -> total tests
        try:
            nan  =  df.index[df.isna().all(axis=1)][0]
        except IndexError:
            nan = None 
            
        # Get index for EP-ASP tests, as they have different DFs
        if nan == None:
            nan = len(df.isna().all(axis=1))
            
        old_t = 0
        
        df2 = df.filter(regex='script')
        
        # Append the times to construct tex file
        times=[0]
        cols = list(df.columns)
        for i in range(len(cols)):
            if(cols[i] and cols[i][:6] =='script' ):
                times.append(i)
            elif cols[i] == "Times":
                times.append(i)
                

        run_df = df.iloc[1:nan, times]

        mini_df = run_df.iloc[:, 1:]
        # print(mini_df)
        total = mini_df.mean(axis=1)
        # print(total)

        run = {}
        run["eligible"] = list(total)
        return list(total)

    
    # df is a list of DataFrames
    def get_3df(self, dfs):
        runs = {}
        for df in dfs:
            print("get3df------",df[1])
            runs[df[1]] = self.do_get_3df(df[0])
        return runs
    
    
    
    def read_ods(self, _file):  # absolute path with .ods at the end
        import os
        # os.system("soffice -env:UserInstallation=file:///$HOME/.libreoffice-headless/ --headless --convert-to xlsx " + _file)
        xlsx = "xperiments/results/" + _file.rsplit('/', 1)[1][:-3] + "xlsx"
        instance_name = Path(_file).stem
        
        # # Save the data to an XLSX file
        # data = pe.get_array(file_name=_file)
        # pe.save_as(array=data, dest_file_name='output.xlsx')
        # xlsx = os.path.splitext(_file)[0] + '.xlsx'
        # instance_name = Path(_file).stem
        # print(instance_name)
        
        return [pd.read_excel(xlsx), instance_name]
    
    def read_many_ods(self, files):
        return self.get_3df([self.read_ods(_file) for _file in files])

    def get_series(self, times, time_range):

        
        counts = {}
        times.sort()

        j=0
        count = 0


        for t in time_range:

            while j<len(times) and times[j]< t:
                count+=1
                j+=1

            counts[t] = count

        return counts

def run(files, solver_names):

    a = Analyzer()

    # Obtain all running times for all battery of tests included.
    times = a.read_many_ods(files)
    print("t--------",times)
    print(len(times))
    print(solver_names)
    all_times = list(itertools.chain.from_iterable(times.values()))

    all_times.sort()
    print("How many:", len(all_times))
    max_time = float(math.ceil(max(all_times))) # Get which is the maximum time for running.
    
    max_time = 600
    exponent, time = 0,0
    tr = ['0']
    while time < max_time:
        time = 2**exponent
        tr.append(str(time))
        exponent+=1

    # time_range = [i for i in range(0, max_time+1, max_time/10)]
    # time_range = [x * 0.1 for x in range(0, 10)] # Yale Shooting problem
    # time_range_str = [str(i) for i in range(0, max_time+1, max_time//10)]
    time_range_str = [str(i) for i in range(0, max_time+1, 1)]
    time_range_str = ','.join(time_range_str)

    tex= f'''
\\documentclass{{standalone}}

\\usepackage{{pgfplots}}

\\pgfplotsset{{compat = newest}}

\\begin{{document}}
\\begin{{tikzpicture}}
\\begin{{axis}}[
    title={{Survival Plots for solvers}},
    ylabel={{Time(Seconds)}},
    xlabel={{#No of Instances solved}},
    ymin=0, ymax=603,
    xmin=0, xmax=225,
    ytick={{0,60,120,180,240,300,360,420,480,540,600}},
    xtick={{40, 80, 120, 160, 200, 220}},
    legend pos=north west,
    ymajorgrids=true,
    grid style=dashed,
]
'''

    for j, t in enumerate(times):

        ti = times[t]

        ti.sort()

        coordinates = []
        for i in range(len(ti)):
            s = "(" + str(i+1) + "," +  str(ti[i]) + ")"
            coordinates.append(s)


        coordinates_str = ''.join(coordinates)

        tex += f'''
        \\addplot[
        color=blue,
        mark=*,
        ]
        coordinates {{
        {coordinates_str}
        }};
        \\addlegendentry{{ {solver_names[j]} }}
        '''

        
    tex += f'''
\end{{axis}}
\end{{tikzpicture}}
\end{{document}}
    '''

    f = open("xperiments/results/SolvingTime_comparison_328P.tex", "w")
    f.write(tex)
    f.close()
    
# TODO: Fix manual conversion of ods to xlsx without sudo privileges
if __name__ == "__main__": 
    solvers = ["G1", "G0"]
    
    run(["xperiments/results/eclingo_reif_(YBE)_Propagate_SolvingTime.ods",
         "xperiments/results/eclingo_reif_(YBE)_NO_Propagate_SolvingTime.ods"], solvers)




    