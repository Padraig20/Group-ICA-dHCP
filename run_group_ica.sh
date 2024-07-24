#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <input_directory> <number_of_components>"
    echo "Example: $0 input 42"
    exit 1
fi

INPUT_DIR=$1
NUM_COMPONENTS=$2

if [ -z "$FSLDIR" ]; then
    echo "Error: FSLDIR is not set. Please source the FSL configuration script."
    exit 1
fi

source $FSLDIR/etc/fslconf/fsl.sh

if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: Input directory $INPUT_DIR does not exist."
    exit 1
fi

cd "$INPUT_DIR" || exit

for dir in */; do
    if [ -d "$dir" ]; then
        echo "Processing directory: $dir"
        cd "$dir" || exit

        mkdir -p output
        melodic -i all_subjects.nii.gz -o output --nobet -d "$NUM_COMPONENTS" --tr=0.392 --report --verbose #--nomask 

        # Check if the MELODIC command was successful
        if [ $? -eq 0 ]; then
            echo "Successfully ran group ICA."
        else
            echo "Error: MELODIC command failed."
            exit 1
        fi

        cd ..
    fi
done

