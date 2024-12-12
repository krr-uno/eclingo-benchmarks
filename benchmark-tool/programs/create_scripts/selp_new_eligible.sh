#!/bin/bash

# Convert new eligible tests from the set of facts into elps files for SELP

# Input directory containing the .lp files
input_dir="benchmarks/new_eligible"

# Output directory for the .elps files
output_dir="selp/selp-benchmarks/newEligibleK"

# Create the output directory if it does not exist
mkdir -p "$output_dir"

# Content to append to each new .elps file
append_content="
predicates
eligible(#s1).
interview(#s1).
highGPA(#s1).
fairGPA(#s1).
minority(#s1).
student(#s1).
lowGPA(#s1).

rules
eligible(X) :- highGPA(X).
eligible(X) :- minority(X), fairGPA(X).
-eligible(X) :- -fairGPA(X), -highGPA(X).
interview(X) :- not K\$ eligible(X), not K\$ -eligible(X)."

# Iterate over each .lp file in the input directory
for file in "$input_dir"/*.lp; do
  # Get the filename without the directory path
  filename=$(basename "$file")
  
  # Get the filename without the .lp extension
  filename_no_ext="${filename%.lp}"
  
  # Count the number of times the word "student" appears in the file
  student_count=$(grep -o -i "student" "$file" | wc -l)
  
  # Create the second line content with incrementing s1, s2, s3, etc.
  second_line="#s1={$(seq -s ', ' -f "s%.0f" 1 $student_count)}."
  
  # Create the output file path with .elps extension
  output_file="$output_dir/$filename_no_ext.elps"
  
  # Write the required lines to the output file
  {
    echo "sorts"
    echo "$second_line"
    echo "$append_content"
    echo
    cat "$file"
  } > "$output_file"
done

echo "Processing complete."

