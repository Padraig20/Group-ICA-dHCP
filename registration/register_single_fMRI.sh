#!/bin/bash

# This script provides a way to register fMRI timepoints to a template image.

set -e

for cmd in fslmaths antsRegistrationSyNQuick.sh antsApplyTransforms fslroi fslmerge fslval parallel ResampleImage; do
    if ! command -v $cmd &> /dev/null; then
        echo "Error: $cmd could not be found. Please install it before running this script."
        exit 1
    fi
done

if [ "$#" -ne 5 ]; then
    echo "Usage: $0 <input_nifti_file> <output_nifti_file> <template_nifti_file> <num_threads> <target_dim>"
    echo "Example: $0 input.nii.gz output.nii.gz template_t1.nii.gz 4 68x67x45"
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="$2"
TEMPLATE_FILE="$3"
NUM_THREADS="$4"
TARGET_DIM="$5"

echo "Generating a mean 3D image..."
fslmaths "$INPUT_FILE" -Tmean mean_fMRI_3D.nii.gz
if [ $? -ne 0 ]; then
    echo "Error: fslmaths command failed."
    exit 1
fi

echo "Registering mean image..."
antsRegistrationSyNQuick.sh -d 3 -f "$TEMPLATE_FILE" -m mean_fMRI_3D.nii.gz -o output_prefix_
if [ $? -ne 0 ]; then
    echo "Error: antsRegistrationSyNQuick.sh command failed."
    exit 1
fi

mkdir -p registered_timepoints
if [ $? -ne 0 ]; then
    echo "Error: Failed to create directory registered_timepoints."
    exit 1
fi

num_volumes=$(fslval "$INPUT_FILE" dim4)
if [ $? -ne 0 ]; then
    echo "Error: fslval command failed."
    exit 1
fi

#num_volumes=300

echo "Will register $num_volumes timepoints..."

process_volume() {
    i="$1"
    INPUT_FILE="$2"
    TEMPLATE_FILE="$3"
	TARGET_DIM="$4"

    fslroi "$INPUT_FILE" "registered_timepoints/timepoint_${i}.nii.gz" "$i" 1
    if [ $? -ne 0 ]; then
        echo "Error: fslroi command failed for timepoint $i."
        exit 1
    fi

    antsApplyTransforms -d 3 -i "registered_timepoints/timepoint_${i}.nii.gz" \
        -r "$TEMPLATE_FILE" -t output_prefix_1Warp.nii.gz -t output_prefix_0GenericAffine.mat \
        -o "registered_timepoints/timepoint_${i}_registered.nii.gz"
    if [ $? -ne 0 ]; then
        echo "Error: antsApplyTransforms command failed for timepoint $i."
        exit 1
    fi

	ResampleImage 3 "registered_timepoints/timepoint_${i}_registered.nii.gz" \
		"registered_timepoints/timepoint_${i}_registered_resampled.nii.gz" "$TARGET_DIM" 1

    if [ $? -ne 0 ]; then
        echo "Error: ResampleImage command failed for timepoint $i."
        exit 1
    fi

	rm "registered_timepoints/timepoint_${i}.nii.gz" 
	rm "registered_timepoints/timepoint_${i}_registered.nii.gz" 

    echo "Timepoint $i finished..."
}

export -f process_volume

parallel -j "$NUM_THREADS" process_volume ::: $(seq 0 2 $(($num_volumes - 1))) ::: "$INPUT_FILE" ::: "$TEMPLATE_FILE" ::: "$TARGET_DIM"

echo "Finished! Now merging files..."
fslmerge -t "$OUTPUT_FILE" $(ls registered_timepoints/timepoint_*_registered_resampled.nii.gz | sort -V)
if [ $? -ne 0 ]; then
    echo "Error: fslmerge command failed."
    exit 1
fi

echo "All done, now let me clean up a bit..."
rm -rdf registered_timepoints
rm -f output_prefix_*
rm -f mean_fMRI_3D.nii.gz

echo "Done! Thanks for the wait!"

