#!/bin/bash

base_url="https://gin.g-node.org/BioMedIA/dhcp-volumetric-atlas-groupwise/raw/master/mean"

echo "This script will download the mask files for gestational ages 36 to 44..."
echo "Make sure you are in the main directory of the project!"

echo "Do you want to create a folder 'metadata/masks'? (y/n)"
read create_folder

if [[ "$create_folder" == "y" ]]; then
  mkdir -p metadata/masks
  echo "Folder 'metadata/masks' created successfully."
else
  echo "Skipped creating folder 'metadata/masks', exiting..."
  exit 1
fi

cd metadata/masks || exit 1

# gestational ages range from 36 to 44
for ga in {36..44}; do
  echo "Do you want to download the file for gestational age ${ga}? (y/n)"
  read user_input

  if [[ "$user_input" == "y" ]]; then
    file_url="${base_url}/ga_${ga}/mask.nii.gz"
    
    wget -O "mask_ga_${ga}.nii.gz" "$file_url"
    
    if [[ $? -eq 0 ]]; then
      echo "Downloaded and renamed mask_ga_${ga}.nii.gz successfully."
    else
      echo "Failed to download mask_ga_${ga}.nii.gz."
    fi
  else
    echo "Skipped download for ga_${ga}."
  fi
done
