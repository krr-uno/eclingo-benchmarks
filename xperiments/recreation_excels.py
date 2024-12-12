import os
import sys
import shutil
import pandas as pd
import xml.etree.ElementTree as ET
import numpy as np
from odf.opendocument import load
from odf.table import Table, TableRow, TableCell

# Define constants
TARGET_ENV_ECLINGO_OLD = "eclingo_old"
TARGET_ENV_ECLINGO_REIF = "eclingo_reif"

# Retrieve the current directory and the environment
current_dir = os.getcwd()  # Replace with the actual directory if needed
CONDA_DEFAULT_ENV = os.environ.get("CONDA_DEFAULT_ENV", "")

# Define function to convert ODS to DataFrame
def ods_to_df(ods_path, dir_errors):
    doc = load(ods_path)
    sheet = doc.spreadsheet.getElementsByType(Table)[0]
    
    # Define column names
    column_names = ["name", "script-0/one", "script-0/two", "max", "median", "min"]
    time_columns = ["name", "time", "time", "time", "time", "time"]
    
    data = []
    for row_idx, row in enumerate(sheet.getElementsByType(TableRow)):
        cells = row.getElementsByType(TableCell)
        
        cell_names = []
        for i, cell in enumerate(cells):
            # Handle cell names for header rows
            if row_idx == 0:
                cell_names.append(str(column_names[i]))
            elif row_idx == 1:
                cell_names.append(str(time_columns[i]))
            else:
                # Append the names of first column cell
                cell_names.append(str(cell))
                
            # Get value from cell
            value = cell.getAttribute("value") or cell.getAttribute("stringvalue") or ""
                
            # Ensure value is a string before calling strip()
            if value is not None:
                value = value.strip()
            
            # Convert value to float if possible, otherwise keep as string
            try:
                value = float(value) if value else ""
            except ValueError:
                value = value or ""
            
            if isinstance(value, float):
                cell_names.append(value)
            else:
                cell_names.append(value)

        data.append(cell_names)
    
    # Create DataFrame
    data = data[1:-8]
    data = [list(filter(lambda x: x != '', inner_array)) for inner_array in data]
    df = pd.DataFrame(data)
    
    # Drop for times
    df = df.drop(index=0).reset_index(drop=True)

    # Rename columns
    df.columns = column_names
    
    # Drop rows where the 'name' column contains '.gitkeep'. Corner case due to benchmark-tool inheritance.
    df = df[~df['name'].str.contains('.gitkeep', na=False)]
    
    # Set values above 600 to 600 in specified columns
    max_value = 600 # TODO: Testing errors

    # Function to apply the rules. Both tests need to solve for time to be considered as solved.
    def enforce_max(row):
        if pd.notnull(row['script-0/one']) and row['script-0/one'] > max_value:
            row['script-0/one'] = max_value
            row['script-0/two'] = max_value
        elif pd.notnull(row['script-0/two']) and row['script-0/two'] > max_value:
            row['script-0/one'] = max_value
            row['script-0/two'] = max_value
        else:
            row['script-0/one'] = min(row['script-0/one'], max_value) if pd.notnull(row['script-0/one']) else row['script-0/one']
            row['script-0/two'] = min(row['script-0/two'], max_value) if pd.notnull(row['script-0/two']) else row['script-0/two']
        return row

    # Apply the function to each row
    df = df.apply(enforce_max, axis=1)
    
    # Check for errors
    df.loc[df['name'].isin(dir_errors), ['script-0/one', 'script-0/two']] = 600

    # Calculate max, median, and min between 'script-0/one' and 'script-0/two'
    df['max']    = df[['script-0/one', 'script-0/two']].max(axis=1)
    df['median'] = df[['script-0/one', 'script-0/two']].median(axis=1)
    df['min']    = df[['script-0/one', 'script-0/two']].min(axis=1)
    
    print(df)

    return df

# Define paths
def get_paths(experiment_name):
    
    # Corner Case eclingo reif
    if CONDA_DEFAULT_ENV == TARGET_ENV_ECLINGO_REIF and experiment_name == "eclingo_reif":
        source_file = f"{current_dir}/running/benchmark-tool-{experiment_name}/experiments/results/eclingo/eclingo.ods"
    else:
        source_file = f"{current_dir}/running/benchmark-tool-{experiment_name}/experiments/results/{experiment_name}/{experiment_name}.ods"
        
    dest_dir = f"{current_dir}/xperiments/plot"
    temp_dir = "/tmp/conversion"

    if CONDA_DEFAULT_ENV == TARGET_ENV_ECLINGO_OLD:
        dest_file = f"{dest_dir}/{experiment_name}_old.xlsx"
    else:
        dest_file = f"{dest_dir}/{experiment_name}.xlsx"

    return source_file, dest_dir, temp_dir, dest_file

# Main processing function
def process_conversion(experiment_name, dir_errors):
    
    source_file, dest_dir, temp_dir, dest_file = get_paths(experiment_name)

    # Create a temporary directory for conversion
    os.makedirs(temp_dir, exist_ok=True)

    # Copy the file to the temporary directory
    shutil.copy(source_file, temp_dir)

    # Create the destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)

    # Convert .ods to .xlsx
    ods_path = os.path.join(temp_dir, os.path.basename(source_file))
    df = ods_to_df(ods_path, dir_errors)
    df.to_excel(dest_file, index=False)

    # Remove the temporary directory
    shutil.rmtree(temp_dir)

def find_directories_with_error(base_path, error_messages, type_benchmark):
    
    # List to store directories with the error
    error_dirs = []
    
    # Check if the base_path exists and is a directory
    if os.path.isdir(base_path):
        try:
            # Change to the specified base directory
            os.chdir(base_path)
        except Exception as e:
            print(f"Error changing directory: {e}")
            return []
    
    # Iterate over all subdirectories
    for subdir in os.listdir('.'):
        subdir_path = os.path.join(base_path, subdir)
        
        if os.path.isdir(subdir_path):
            # Define the path to the 'runsolver.solver' file
            runsolver_path = os.path.join(subdir_path, 'run1/runsolver.solver')
                
            if os.path.isfile(runsolver_path):
                # Read the content of the file
                with open(runsolver_path, 'r') as file:
                    file_content = file.read()
    
                # Check for the specific error message
                for error in error_messages:
                    if error in file_content:
                        error_at = type_benchmark + "/" + subdir
                        error_dirs.append(error_at)

    
    return error_dirs

def create_solving_time_eclingo(solver_name, excel_path, xml_path, current_dir):
    """
        Parameters
        -----------
            excel_path (str): xlsx file path to use as reference for constructing new xlsx file.
            xml_path (str): beval file path under running and {solver} directory that provides solving times.
    """
    
    # Load the Excel file
    excel_data = pd.read_excel(excel_path)

    # Parse the XML file
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Dictionary to store timing information
    timing_info = {'one': [], 'two': []}
    instance_id_map = {}
    name_occurrence_count = {}

    # Iterate through the XML tree
    for class_elem in root.findall('.//class'):
        class_name = class_elem.get('name')
        class_id = class_elem.get('id')
        
        for instance_elem in class_elem.findall('instance'):
            instance_name = instance_elem.get('name')
            
            instance_id = instance_elem.get('id')
            final_id = class_id + "-" + instance_id
            
            # Populate the instance_id_map dictionary
            if instance_name is not None:
                final_name = class_name + "/" + instance_name
                instance_id_map[final_id] = final_name

            for run_elem in instance_elem.findall('run'):

                time_value = None
                for measure_elem in run_elem.findall('measure'):

                    if measure_elem.get('name') in ['sol-time', 'time']:
                        
                        time_value = float(measure_elem.get('val'))
                        # print(instance_id_map[final_id], final_id, time_value)
                        break
                    
                # Store the timing information
                if time_value is not None:
            
                    # Increment count for the instance name
                    name_count = name_occurrence_count.get(final_id, 0) + 1
                    name_occurrence_count[final_id] = name_count
                    
                    if name_count == 1:
                        timing_info['one'].append({instance_id_map[final_id]: time_value})
                    elif name_count == 2:
                        timing_info['two'].append({instance_id_map[final_id]: time_value})
        
    # Collect rows for DataFrame
    rows = []
    for index, row in excel_data.iterrows():
        name = row['name']
        instance_name = name.split('/')[-1]

        # Extract time values from the timing_info list of dictionaries
        script_one_time = next((item[name] for item in timing_info['one'] if name in item), None)
        script_two_time = next((item[name] for item in timing_info['two'] if name in item), None)
        
        # Trim values over 600
        if script_one_time >= 600 or script_two_time >= 600:
            script_one_time = 600
            script_two_time = 600
            
        # Get the max, min, median values
        times = [script_one_time, script_two_time]
        max_times    = np.max(times)
        min_times    = np.min(times)
        median_times = np.median(times)

        # Collect row data
        rows.append({
            'name': name,
            'script-0/one': script_one_time,
            'script-0/two': script_two_time,
            'max': max_times,
            'median': median_times,
            'min': min_times,
            
        })
        
    # Save the result to a new Excel file
    result_data = pd.DataFrame(rows)
    result_path = f'{current_dir}/xperiments/plot/{solver_name}_solving.xlsx'
    result_data.to_excel(result_path, index=False)

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python recreation_excels.py <solver_name>")
        sys.exit(1)

    # Get Epistemic Solver name
    solver_name = sys.argv[1]
    
    # Corner case for eclingo reif. Change if eclingo_reif does not exist -> 1st time execution.
    basic_dir = os.path.join(current_dir, f"running/benchmark-tool-{solver_name}")
    
    if CONDA_DEFAULT_ENV == TARGET_ENV_ECLINGO_REIF and os.path.exists(basic_dir) and solver_name == "eclingo":
        new_base_directory = os.path.join(current_dir, f"running/benchmark-tool-{TARGET_ENV_ECLINGO_REIF}")
        os.rename(basic_dir, new_base_directory)
        solver_name = TARGET_ENV_ECLINGO_REIF
        
    elif CONDA_DEFAULT_ENV == TARGET_ENV_ECLINGO_REIF and solver_name == "eclingo":
        solver_name = TARGET_ENV_ECLINGO_REIF
        
    # Data cleaning of Epistemic Solver errors due to memory or time constraints.
    base_directory = f"{current_dir}/running/benchmark-tool-{solver_name}/output/project/zuse/results/suite/script-0-one/"
    
    # Error messages
    error_messages = ['qasp: error: std::bad_alloc', 'Killed: Bye!', 'java.lang.ArrayIndexOutOfBoundsException: -1',
                      'Exception in thread "main" java.lang.OutOfMemoryError: Java heap space', 'maximum recursion depth exceeded in comparison',
                      '*** Info : (clingo): INTERRUPTED by signal!', '*** ERROR: (clingo): <python>: error: error calling main function:',
                      'Terminated', 'Exception in thread "main" java.lang.OutOfMemoryError: GC overhead limit exceeded']
    
    directories_with_error = []
    eligible_dir = base_directory + "eligible"
    bomb_dir = base_directory + "bomb_problems"
    
    if solver_name == "qasp":
        
        # Eligible problems check
        directories_with_error = find_directories_with_error(eligible_dir, error_messages, "eligible")
        
        # Bomb Problems check
        directories_with_error += find_directories_with_error(bomb_dir, error_messages, "bomb_problems")
        
    if solver_name == "selp":
        
        # Eligible problems check
        directories_with_error = find_directories_with_error(eligible_dir, error_messages, "eligible")
        
        # Bomb Problems check
        directories_with_error += find_directories_with_error(bomb_dir, error_messages, "bomb_problems")
        
    if solver_name == "ep_asp" or solver_name == "ep_asp_no_planning":
        
        # Eligible problems check
        directories_with_error = find_directories_with_error(eligible_dir, error_messages, "eligible")
        
        # Bomb Problems check
        bomb_dir = base_directory + "bombProblems"
        directories_with_error += find_directories_with_error(bomb_dir, error_messages, "bombProblems")

    # print(f"Solver: {solver_name}:\n{directories_with_error}")
 
    process_conversion(solver_name, directories_with_error)
    
    # Generate solving excels
    if solver_name == "eclingo_reif" or "eclingo-no":
        excel_path = f"{current_dir}/xperiments/plot/{solver_name}.xlsx"
        
        # Corner Case eclingo reif
        if CONDA_DEFAULT_ENV == TARGET_ENV_ECLINGO_REIF and solver_name == "eclingo_reif":
            xml_path = f"{current_dir}/running/benchmark-tool-{solver_name}/experiments/results/eclingo/eclingo.beval"
        else:
            xml_path = f"{current_dir}/running/benchmark-tool-{solver_name}/experiments/results/{solver_name}/{solver_name}.beval"
            
        create_solving_time_eclingo(solver_name, excel_path, xml_path, current_dir)
