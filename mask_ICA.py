import nibabel as nb
import numpy as np
import nilearn.image 
import nilearn.masking

# load the group ICA map
nifti_orig = nb.load('melodic_IC.nii.gz')

# load the mask file
mask_file_nifti = nb.load('mask.nii.gz')
mask_file=mask_file_nifti.get_fdata().astype(int)
print(f"Shape of mask: {mask_file.shape}")

# preprocess the mask to fit the group ICA map
target_affine = nifti_orig.affine
target_shape = nifti_orig.shape[:3]
mask = nilearn.image.resample_img(mask_file_nifti,
                                  target_affine=target_affine, 
                                  target_shape=target_shape,interpolation='nearest')

nb.save(mask,'mask_preprocessed.nii.gz')

print(f"Shape of preprocessed mask: {mask.shape, mask.affine}")

# mask the group ICA map
masked_pixels = nilearn.masking.apply_mask(nifti_orig, mask_img=mask)
print(f"Shape of masked group ICA map: {masked_pixels.shape}")

np.save('dHCP_groupICA_masked.npy', masked_pixels)

