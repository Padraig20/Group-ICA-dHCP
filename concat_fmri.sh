#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

DIR=$1

if [ ! -d "$DIR" ]; then
    echo "Error: $DIR is not a directory"
    exit 1
fi

cd "$DIR" || exit

for dir in */; do
    if [ -d "$dir" ]; then
        echo "Processing directory: $dir"

        cd "$dir" || exit

        FILES=(*.nii.gz)

        if [ ${#FILES[@]} -eq 0 ]; then
            echo "Error: No .nii.gz files found in the directory"
            exit 1
        fi

        fslmerge -t all_subjects.nii.gz "${FILES[@]}"

        if [ $? -eq 0 ]; then
            echo "Successfully concatenated all .nii.gz files into all_subjects.nii.gz"
        else
            echo "Error: fslmerge command failed"
            exit 1
        fi

        cd ..
    fi
done


