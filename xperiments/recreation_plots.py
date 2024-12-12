import os
import pandas as pd
import matplotlib.pyplot as plt
import itertools

def plot_median_values_from_xlsx(directory, label_to_color, label_to_style, filename_to_labels, used_labels, plot_name):

    plt.figure(figsize=(10, 6))

    # Iterate over all files in the specified directory
    for filename in os.listdir(directory):
        if filename.endswith(".xlsx"):
            # Extract the base name without extension
            base_name = os.path.splitext(filename)[0]
            
            # Get the label for the current file, default to the base name if not in mapping
            label = filename_to_labels.get(base_name, base_name)
            
            if label in used_labels:
                print(label)
                color = label_to_color.get(label, None)
                
                # Get the line style and marker for the current label
                linestyle, marker = label_to_style.get(label, ('-', 'o'))
                
                file_path = os.path.join(directory, filename)
                try:
                    # Read the Excel file
                    df = pd.read_excel(file_path)
                    # Extract the 'median' column values
                    if 'median' in df.columns:
                        median_values = df['median'].dropna().tolist()
                        if median_values:
                            median_values.sort()
                            plt.plot(median_values, marker=marker, linestyle=linestyle, label=label, color=color)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

     # Define fixed x and y-axis values
    fixed_y_values = range(0, 660, 60) 
    fixed_x_values = range(0, 400, 50)  

    # Set fixed tick values for x and y axes
    plt.xticks(fixed_x_values)
    plt.yticks(fixed_y_values)
    
    # Add plot details
    plt.title('Survival Plot for Solvers')
    plt.xlabel('Nº of Instances Solved')
    plt.ylabel('Time (Seconds)')
    plt.grid(True)
    plt.legend(loc='lower right')
    plt.savefig(f"xperiments/plot/{plot_name}.png")
   
if __name__ == "__main__":
    
    # Directory containing the XLSX files
    current_dir = os.getcwd()
    directory = f"{current_dir}/xperiments/plot"

    # Define a color mapping for different labels
    label_to_color = {
        'G1': 'blue',
        'eclingo': 'green',
        'EP-ASP^se': 'yellow',
        'EP-ASP': 'purple',
        'selp': 'orange',
        'elp2qasp': 'black'
    }

    # Define line style and marker mapping for different labels
    label_to_style = {
        'G1': ('-', 'o'),           # Full line, circle marker
        'eclingo': ('--', 'o'),     # Broken lines, circle marker
        'EP-ASP^se': ('--', 'x'),   # Broken lines, x marker
        'EP-ASP': ('-', 'x'),       # Full line, x marker
        'selp': (':', 'o'),         # Dotted lines, circle marker
        'elp2qasp': (':', 'd')      # Dotted lines, dotted marker
    }

    # Mapping from filename to legend label
    filename_to_label = {
        'eclingo_reif': 'G1',
        'eclingo_old': 'eclingo',
        'ep_asp': 'EP-ASP^se',
        'ep_asp_no_planning': 'EP-ASP',
        'selp': 'selp',
        'qasp': 'elp2qasp'
    }
    
    # Call the function to generate the plot
    plot_name = "All_solvers_comparison"
    used_labels = ['G1', 'eclingo', 'EP-ASP^se', 'EP-ASP', 'selp', 'elp2qasp']
    # plot_median_values_from_xlsx(directory, label_to_color, label_to_style, filename_to_label, used_labels, plot_name)
    
    # Define a color mapping for different labels
    label_to_color = {
        'G1': 'blue',
        'G0': 'red'
    }

    # Define line style and marker mapping for different labels
    label_to_style = {
        'G1': ('-', 'o'),  # Full line, circle marker
        'G0': (':', 'x')   # Dotted line, x marker
    }

    # Mapping from filename to legend label
    filename_to_label = {
        'eclingo_reif_solving': 'G1',
        'eclingo-no_solving': 'G0'
    }
    
    plot_name = "Solver_Reification_Propagate_Comparison"
    used_labels = ['G1', 'G0']
    plot_median_values_from_xlsx(directory, label_to_color, label_to_style, filename_to_label, used_labels, plot_name)
    
