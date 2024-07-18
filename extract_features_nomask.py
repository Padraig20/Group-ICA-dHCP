#Dual regression and connectivity map extraction for rs-fMRI.

from conntask_ni import utils
import nibabel as nb
import numpy as np
import os
import time
import nilearn.masking
from scipy.signal import detrend
from sklearn.preprocessing import StandardScaler

##################################################################################
################ SOURCE: https://github.com/ShacharGal/connTask ##################
##################################################################################

def read_nii(entry):
    if isinstance(entry, np.ndarray):
        return entry # the object is already the img
    img = nb.load(entry)
    return np.asarray(img.get_fdata())

def read_multiple_ts_data(file_paths, trim=None):
    # reads multiple time series files, normalizes, demeans and concatenates
    # trim is used if you do not wish to use all the time points in your data
    all_data = []
    for file_path in file_paths:
        rs = read_nii(file_path).T # original file should be (time,voxels)
        if isinstance(trim, np.ndarray):
            rs = rs[:, trim]
        all_data.append(detrend(StandardScaler().fit_transform(rs)))
    return np.concatenate(all_data, axis=1)

def parse_dr_args(data, components):
    # read data and make sure its in the right dimensions for further processing
    if isinstance(data, list):
        data = utils.read_multiple_ts_data(data)
    elif isinstance(data, str):
        rs = utils.read_data(data).T
        data = detrend(StandardScaler().fit_transform(rs))
    elif isinstance(data, np.ndarray):
        if data.shape[0] < data.shape[1]:
            data = data.T # data should be nvoxels * nica_components
    else:
        warnings.warn('data is supplied in unknown format')

    if isinstance(components, str):
        components = utils.read_data(components).T
    elif isinstance(components, np.ndarray):
        pass
    else:
        print('ica components should be a path to an nii file or an nd.array')
        raise TypeError
    if components.shape[0] < components.shape[1]:
        components = components.T # group ica file should be nvoxels * nica_components
    return data, components

def dual_regression(data, group_components):
    # perform dual regression to yield subject-specific spatial-components
    data, group_components = parse_dr_args(data, group_components)
    # step 1: get components subject-specific time series for each components
    pinv_comp = np.linalg.pinv(group_components)
    ts = np.matmul(pinv_comp, data)
    # step 2: find the subject-specific spatial pattern for each component
    sub_comps = utils.fsl_glm(ts.T, data.T)
    return sub_comps.T

def weighted_seed2voxel(seeds, data):
    # performs a weighted_seed2voxel analysis for each component
    # to yield the connectivity maps used in the connTask prediction pipeline
    pinv_seeds = np.linalg.pinv(seeds)
    ts = np.matmul(pinv_seeds, data)
    ts_norm = utils.normalise_like_matlab(ts.T).T
    data_norm = utils.normalise_like_matlab(data.T).T
    features = np.matmul(ts_norm, data_norm.T).T
    return features

##################################################################################
##################################################################################
##################################################################################

from argparse import ArgumentParser

parser = ArgumentParser(description='Script used to perform dual regression and connectivity map regression for resting state fMRI. Output can be used as input to SwiFUN. Group ICA file is required to be produced by MELODICA and masked via the mask_ICA.py script.')
parser.add_argument('--groupICA_file', default='dHCP_groupICA_masked.npy', type=str, help='Assume that the group ICA file is registered, masked, and flattened. (dim: # component * # voxels except backgrounds), made in mask_ICA.py')
parser.add_argument('--outdir', default='out/features', type=str)
parser.add_argument('--start_idx', default=0, type=int)
parser.add_argument('--maskdir', default='mask_preprocessed.nii.gz', type=str,help='Must be produced in mask_ICA.py')
parser.add_argument('--rs_data_dir', default='img', type=str)
parser.add_argument('--rs_output_file', default='features_42_comps', type=str,help='Name suffix of the output file for the resting state features')

args = parser.parse_args()

if not os.path.exists(args.outdir):
    create_dir = input("Output directory does not exist. Do you want to create it? (y/n): ")
    if create_dir.lower() == "y":
        os.makedirs(args.outdir)
        print(f"Output directory '{args.outdir}' created.")
    else:
        print("Output directory does not exist and user chose not to create it. Exiting...")
        exit()

print()
print('-'*60)
print('-'*60)
print(f'Data will always be reshaped from (x,y,z,c) to (c, x*y*z)!')
print('Make sure that c are the number of independent components...')
print('-'*60)
print('-'*60)
print()

print('Loading group ICA...')
group_ica = nb.load(args.groupICA_file)

print(f'Reshaping group ICA with dimensions {group_ica.shape}...')
group_ica_data = group_ica.get_fdata()
group_ica = np.reshape(group_ica_data, (-1, group_ica_data.shape[-1])).T
print(f'Successfully reshaped group ICA: {group_ica.shape}')

# set an output directory for the features
outdir = args.outdir

# set origin directory for raw data
rs_data_dir = args.rs_data_dir
#mask = nb.load(args.maskdir)

# iterate through all participants and perform feature extraction
subjects = [ subj for subj in os.listdir(rs_data_dir) ]

for i, sub in enumerate(sorted(subjects)[args.start_idx:]):
    rs_file = f'{rs_data_dir}/{sub}'
    print(f'subject {i+1}/{len(subjects)}: {sub[:15]}')
    start=time.time()
    try:
        if not os.path.exists(f'{outdir}/{sub[:15]}_{args.rs_output_file}.npy'): 
            print(f'\tLoading image...')
            rs_image = nb.load(rs_file)
            rs_data = rs_image.get_fdata()

            print(f'\tReshaping data from (x,y,z,p) to (c,x*y*z)...')
            # Reshape the data from (x, y, z, t) to (t, x*y*z)
            reshaped_data = np.reshape(rs_data, (-1, rs_data.shape[-1])).T
            rs_paths = [reshaped_data]
            
            print(f'\tReshaped data successfully from {rs_data.shape} to {reshaped_data.shape}!')
        
            data = read_multiple_ts_data(rs_paths)

            # perform two steps of feature extraction
            print('\tExtracting features...')
            dr_comps = dual_regression(data, group_ica)
            features = weighted_seed2voxel(dr_comps, data)

            print('\tSaving features...')
            to_save = features.T
            np.save(f'{outdir}/{sub[:15]}_{args.rs_output_file}', to_save)
        else:
            print('\tFile already exists!')
    except Exception as e:
        print(f'\tHaving problems in file {sub}...')
        print(f'\tFollowing error occured: {e}')
        with open('corrupted_files.txt','a') as f:
            f.write(f'{sub}\n')
    end=time.time()
    print(f'\tTime taken to process {sub[:15]}: {end-start}')
