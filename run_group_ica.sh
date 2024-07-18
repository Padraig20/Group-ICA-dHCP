#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <input_file> <output_directory> <number_of_components>"
    echo "Example: $0 all_subjects.nii.gz groupICA_output_directory 42"
    exit 1
fi

INPUT_FILE=$1
OUTPUT_DIR=$2
NUM_COMPONENTS=$3

if [ -z "$FSLDIR" ]; then
    echo "Error: FSLDIR is not set. Please source the FSL configuration script."
    exit 1
fi

source $FSLDIR/etc/fslconf/fsl.sh

if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file $INPUT_FILE does not exist."
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

#melodic -i "$INPUT_FILE" -o "$OUTPUT_DIR" --nobet --bgimage=$FSLDIR/data/standard/MNI152_T1_2mm_brain -d "$NUM_COMPONENTS" --tr=0.392 --report
melodic -i "$INPUT_FILE" -o "$OUTPUT_DIR" --nobet -d "$NUM_COMPONENTS" --tr=0.392 --report --verbose #--nomask 

# Check if the MELODIC command was successful
if [ $? -eq 0 ]; then
    echo "Successfully ran group ICA. Results are saved in $OUTPUT_DIR"
else
    echo "Error: MELODIC command failed."
    exit 1
fi

