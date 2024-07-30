from conntask_ni import utils
import nibabel as nb
import numpy as np
import pandas as pd
import os
import time
import nilearn.masking
from scipy.signal import detrend
from sklearn.preprocessing import StandardScaler
import warnings
import atexit
from colorama import Fore, Style, init

init()

captured_warnings = []

def display_warnings():
    if captured_warnings:
        print()
        print(Fore.YELLOW + "-"*30 + " WARNING " + "-"*30)
        for warning in captured_warnings:
            print(f"{warning.category.__name__}: {warning.message}")

atexit.register(display_warnings)

def load_nifti(path):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        file = nb.load(path)
        captured_warnings.extend(w)
        return file

def fit_mask(mask_file_nifti, img):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        target_affine = img.affine
        target_shape = img.shape[:3]
        mask = nilearn.image.resample_img(mask_file_nifti,
                                        target_affine=target_affine, 
                                        target_shape=target_shape, interpolation='nearest')
        print(f'\tApplying transformed mask {mask.shape} to image {img.shape}...')
        masked_pixels = nilearn.masking.apply_mask(img, mask_img=mask)
        print(f'\tShape of masked image: {masked_pixels.shape}')
        captured_warnings.extend(w)
        return masked_pixels, mask

from argparse import ArgumentParser

parser = ArgumentParser(description='Script used to create masks for ICA components, also to mask the group ICA maps.')
parser.add_argument('--groupICA_dir', default='registered_input-test', type=str, help='Assume that the group ICA files are registered and flattened (dim: # component * # voxels except backgrounds). Assumed to be in directory "output" and called "melodic_IC.nii.gz".')
parser.add_argument('--out_maskdir', default='metadata/ica_masks', type=str)
parser.add_argument('--maskdir', default='metadata/masks', type=str,help='Use the masks you can download from the dHCP website; use the script. It will be preprocessed on the flight for each separate image.')

args = parser.parse_args()

if not os.path.exists(args.out_maskdir):
    create_dir = input("Output directory does not exist. Do you want to create it? (y/n): ")
    if create_dir.lower() == "y":
        os.makedirs(args.out_maskdir)
        print(Fore.GREEN + f"Output directory '{args.out_maskdir}' created.")
    else:
        print(Fore.RED + "Output directory does not exist and user chose not to create it. Exiting...")
        exit()
        
for dir in os.listdir(args.groupICA_dir):
    dir_path = os.path.join(args.groupICA_dir, dir)
    if os.path.isdir(dir_path):
        print(f"Processing {dir_path}...")

        gestational_age = int(dir.split('_')[1]) # ga_XX
        mask_file = os.path.join(args.maskdir, f'mask_ga_{gestational_age}.nii.gz')
        mask_file_nifti = load_nifti(mask_file)
        groupICA_file = os.path.join(dir_path, 'output', 'melodic_IC.nii.gz')
        groupICA_file_nifti = load_nifti(groupICA_file)
        
        masked_pixels, mask = fit_mask(mask_file_nifti, groupICA_file_nifti)
                        
        np.save(os.path.join(dir_path, 'output', 'melodic_IC_masked.npy'), masked_pixels)
        
        output_file = os.path.join(args.out_maskdir, f'mask_ga_{gestational_age}.nii.gz')
        nb.save(mask, output_file)
        
        print(f"Finished processing {dir_path}.")

print("Finished processing all group ICA directories.")