#!/bin/bash

# This script provides a way to register fMRI timepoints to a template image. Scans a whole directory of fMRI timepoints
# and registers each one to specified template image.

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <input_dir> <template_file> <num_threads>"
    echo "Example: $0 input t1-template.nii.gz 4"
    exit 1
fi

INPUT_DIR="$1"
TEMPLATE_FILE="$2"
NUM_THREADS="$3"
TARGET_DIM="$4"

if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: $INPUT_DIR is not a directory"
    exit 1
fi

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "Error: $INPUT_FILE does not exist or is not a file"
    exit 1
fi

mkdir -v registered_"$INPUT_DIR"
if [ $? -ne 0 ]; then
    echo "Error: Failed to create output directory: registered_$file"
    exit 1
fi

mkdir -v .temp-registration-processing
if [ $? -ne 0 ]; then
    echo "Error: Failed to create temporary working directory: .temp-registration-processing"
    exit 1
fi
cd .temp-registration-processing || exit 1

for file in "../$INPUT_DIR"/*.nii.gz; do
    if [ -f "$file" ]; then
        echo "Processing file: $file"

        file_name=$(basename "$file")

        ../registration/register_single_fMRI.sh "$file" "../registered_$INPUT_DIR/$file_name" "../$TEMPLATE_FILE" "$NUM_THREADS"

        if [ $? -ne 0 ]; then
            echo "Error: Failed to register $file"
            echo "$file" >> ../failed_registration.txt
            echo "Deleting contents of temporary working directory..."
            rm -rdf *
            continue
        fi

    fi
done

echo "Okay, I'm done with registration. Cleaning up..."

cd ..
rm -rdf .temp-registration-processing

echo "Registration complete, thanks for waiting!"