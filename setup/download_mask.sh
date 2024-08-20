#!/bin/bash

base_url="https://gin.g-node.org/BioMedIA/dhcp-volumetric-atlas-groupwise/raw/master/mean"

echo "This script will download the t1 template files for gestational age 40..."
echo "Make sure you are in the main directory of the project!"
echo "Will put the file into 'metadata' folder."

cd metadata || exit 1

echo "Do you want to download the mask for gestational age 40? (y/n)"
read user_input

if [[ "$user_input" == "y" ]]; then
  file_url="${base_url}/ga_40/mask.nii.gz"
    
  wget -O "mask_ga_40.nii.gz" "$file_url"
    
  if [[ $? -eq 0 ]]; then
    echo "Downloaded and renamed mask_ga_40.nii.gz successfully."
  else
    echo "Failed to download mask_ga_40.nii.gz."
  fi
  else
    echo "Okayyyyyy, bye bye"
fi
