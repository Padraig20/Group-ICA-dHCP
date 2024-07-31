#!/bin/bash

# This script provides a way to register fMRI timepoints to a template image.
# When generating registered images via register_multiple_fMRI.sh, some images may fail to register.
# This script can be used to register the failed images.
# The failed images are listed in the file failed_registration.txt in the output directory.
# The script will attempt to register the failed images and write to the failed_registration_retry.txt file with any images that still fail.
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

if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <input_txt_file> <template_dir> <num_threads> <target_dim>"
    echo "Example: $0 failed_registrations.txt t1-templates 4 68x67x45"
    exit 1
fi

INPUT_FILE="$1"
TEMPLATE_DIR="$2"
NUM_THREADS="$3"
TARGET_DIM="$4"

if [ ! -d "$TEMPLATE_DIR" ]; then
    echo "Error: $TEMPLATE_DIR is not a directory"
    exit 1
fi

mkdir -v retried_registration
if [ $? -ne 0 ]; then
    echo "Error: Failed to create output directory: retried_registration"
    exit 1
fi

mkdir -v .temp-retried-registration-processing
if [ $? -ne 0 ]; then
    echo "Error: Failed to create temporary working directory: .temp-retried-registration-processing"
    exit 1
fi
cd .temp-retried-registration-processing || exit 1

while IFS= read -r file; do
    echo "Processing file: $file"

    # assume names ../<input_dir>/ga_XX/<filename>
    file_name=$(basename "$file")
    dir_name=$(dirname "$file")
    dir_name=$(basename "$dir_name")
    dir_name=${dir_name#*_}

    ../registration/register_single_fMRI.sh "$file" "../retried_registration/$dir_name/$file_name" "../$TEMPLATE_DIR/template_t1_$dir_name.nii.gz" "$NUM_THREADS" "$TARGET_DIM"

    if [ $? -ne 0 ]; then
        echo "Error: Failed to register $file"
        echo "$file" >> ../failed_registration_retried.txt
        echo "Deleting contents of temporary working directory..."
        rm -rdf *
        continue
    fi

done < $INPUT_FILE

cd ..
rm -rdf .temp-retried-registration-processing

echo "Registration complete, thanks for waiting!"