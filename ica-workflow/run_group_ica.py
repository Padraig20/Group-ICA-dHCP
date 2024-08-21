import os
import sys
from fsl.wrappers import melodic
import fsl.utils.run as run

def main(input_dir, num_components):

    if not os.path.isdir(input_dir):
        print(f"Error: Input directory {input_dir} does not exist.")
        sys.exit(1)

    output_dir = os.path.join(input_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)

    try:
        melodic(
            input=os.path.join(input_dir, 'all_subjects.nii.gz'),
            outdir=output_dir,
            nobet=True,
            dim=num_components,
            tr=0.392,
            report=True,
            verbose=True
        )
        print("Successfully ran group ICA.")
    except run.FSLRuntimeError as e:
        print(f"Error: MELODIC command failed. {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <input_directory> <number_of_components>")
        print(f"Example: python {sys.argv[0]} input 42")
        sys.exit(1)

    input_dir = sys.argv[1]
    num_components = int(sys.argv[2])

    main(input_dir, num_components)
