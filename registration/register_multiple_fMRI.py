import os
import sys
from pathlib import Path
from register_single_fMRI import main as register_single_fMRI
from tqdm import tqdm
import contextlib

@contextlib.contextmanager # for visual cleanliness
def suppress_output():
    """Suppress stdout and stderr."""
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

def process_registration(input_dir, template_file, num_threads):
    output_dir = f'registered_{input_dir}'
    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        print(f"Error: Failed to create output directory: {output_dir}\n{e}")
        sys.exit(1)

    input_dir_path = Path(input_dir)
    failed_files = []
    files_to_process = list(input_dir_path.glob('*.nii.gz'))
    
    with tqdm(total=len(files_to_process), desc="Processing files", unit="file", dynamic_ncols=True) as pbar:
        for file in files_to_process:
            if file.is_file():
                pbar.set_description(f"Processing {file.name}")
                output_file = Path(output_dir) / file.name

                try:
                    with suppress_output(): # simply for visual cleanliness
                        register_single_fMRI(str(file), str(output_file), template_file, num_threads)
                    
                except Exception as e:
                    print(f"\nError: Failed to register {file}\n{e}")
                    failed_files.append(file)

                pbar.update(1)
    
    if failed_files:
        with open('failed_registration.txt', 'w') as f:
            for failed_file in failed_files:
                f.write(f"{failed_file}\n")
        print(f"Registration completed with errors. See failed_registration.txt for details.")
    else:
        print("Registration complete, thanks for waiting!")

def main():
    if len(sys.argv) != 4:
        print("Usage: python script.py <input_dir> <template_file> <num_threads>")
        print("Example: python script.py input t1-template.nii.gz 4")
        sys.exit(1)

    input_dir = sys.argv[1]
    template_file = sys.argv[2]
    num_threads = sys.argv[3]

    if not os.path.isdir(input_dir):
        print(f"Error: {input_dir} is not a directory")
        sys.exit(1)

    if not os.path.isfile(template_file):
        print(f"Error: {template_file} does not exist or is not a file")
        sys.exit(1)

    process_registration(input_dir, template_file, num_threads)

if __name__ == "__main__":
    main()
