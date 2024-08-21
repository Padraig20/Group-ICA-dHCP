import os
import sys
import nibabel as nib
from nilearn.image import concat_imgs
from tqdm import tqdm

def main(directory):
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a directory")
        sys.exit(1)

    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.nii.gz')]

    if len(files) == 0:
        print("Error: No .nii.gz files found in the directory")
        sys.exit(1)

    try:
        concatenated_img = concat_imgs(tqdm(files, desc="Concatenating files"))

        output_file = os.path.join(directory, 'all_subjects.nii.gz')
        
        print(f"Saving concatenated image to {output_file}")
        
        nib.save(concatenated_img, output_file)

        print(f"Successfully concatenated all .nii.gz files into {output_file}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    main(directory)
