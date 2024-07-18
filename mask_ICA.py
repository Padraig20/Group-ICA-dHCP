import nibabel as nb
import numpy as np
import argparse
import nilearn.image 
import nilearn.masking

parser = argparse.ArgumentParser(description='Masking the group ICA map')

parser.add_argument('--input', type=str, help='Path to the group ICA map created by MELODIC', default='output/melodic_IC.nii.gz')
parser.add_argument('--mask', type=str, help='Path to the mask nifti file', default='mask.nii.gz')
parser.add_argument('--output', type=str, help='Path to save the masked group ICA map as npy file', default='dHCP_groupICA_masked.npy')

args = parser.parse_args()

# load the group ICA map
nifti_orig = nb.load(args.input)

# load the mask file
mask_file_nifti = nb.load(args.mask)
mask_file = mask_file_nifti.get_fdata().astype(int)
print(f"Shape of mask: {mask_file.shape}")

# preprocess the mask to fit the group ICA map
target_affine = nifti_orig.affine
target_shape = nifti_orig.shape[:3]
mask = nilearn.image.resample_img(mask_file_nifti,
                                  target_affine=target_affine, 
                                  target_shape=target_shape, interpolation='nearest')

nb.save(mask, f'{args.mask[:-7]}_preprocessed.nii.gz')

print(f"Shape of preprocessed mask: {mask.shape, mask.affine}")

# mask the group ICA map
masked_pixels = nilearn.masking.apply_mask(nifti_orig, mask_img=mask)
print(f"Shape of masked group ICA map: {masked_pixels.shape}")

np.save(args.output, masked_pixels)

