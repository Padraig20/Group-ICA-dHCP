#!/bin/bash

# This script provides a way to register fMRI timepoints to a template image. Scans a whole directory of fMRI timepoints
# and registers each one to the gestational age-specific template image.
# The input directory is required to have a specific structure:
# input_dir
# ├── ga_36
# │   ├── subject1.nii.gz
# │   ├── subject2.nii.gz
# │   └── ...
# └── ...
# └── ga_44
#     ├── subject1.nii.gz
#     ├── subject2.nii.gz
#     └── ...
# The output directory will have the same structure as the input directory, but with the registered fMRI images.

set -e

if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <input_dir> <template_dir> <num_threads> <target_dim>"
    echo "Example: $0 input t1-templates 4 68x67x45"
    exit 1
fi

INPUT_DIR="$1"
TEMPLATE_DIR="$2"
NUM_THREADS="$3"
TARGET_DIM="$4"

if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: $INPUT_DIR is not a directory"
    exit 1
fi

if [ ! -d "$TEMPLATE_DIR" ]; then
    echo "Error: $TEMPLATE_DIR is not a directory"
    exit 1
fi

mkdir -v registered_"$INPUT_DIR"

mkdir -v .temp-registration-processing
cd .temp-registration-processing || exit 1

for dir in "../$INPUT_DIR"/*; do
    if [ -d "$dir" ]; then
        echo "Processing directory: $dir"

        dir_name=$(basename "$dir")

        mkdir -v "../registered_$INPUT_DIR/$dir_name"

        for file in "$dir"/*.nii.gz; do
            if [ -f "$file" ]; then
                echo "Processing file: $file"

                file_name=$(basename "$file")

                ../registration/register_single_fMRI.sh "$file" "../registered_$INPUT_DIR/$dir_name/$file_name" "../$TEMPLATE_DIR/template_t1_$dir_name.nii.gz" "$NUM_THREADS" "$TARGET_DIM"

                if [ $? -ne 0 ]; then
                    echo "Error: Failed to register $file"
                    echo "$file" >> failed_registration.txt
                    continue
                fi

            fi
        done
    fi
done

cd ..
rm -rdf .temp-registration-processing

echo "Registration complete, thanks for waiting!"