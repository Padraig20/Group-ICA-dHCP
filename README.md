# Grouped Independent Component Analysis (ICA) for the developing Human Connectome Project (dHCP)
The goal is to perform grouped Independent Component Analysis (ICA) to extract meaningful signals from neonatal brains via the developing Human Connectome Project (dHCP). These Independent Components are planned to be used as an input for SwiFUN, to extract task-related information from resting-state functional Magnetic Resonance Images (rsfMRI).

## Project Structure

```
Group-ICA-dHCP
├── ica-workflow                       <- contains the whole workflow for generating ICA features
│   └── run_group_ica.sh/.py           <- step 1: performs approximated ICA via MIGP on the fMRI volumes, outputs group ICA map
│   ├── create_masks.py                <- step 2: masks the group ICA map and saves the mask which will be used during SwiFT training and feature extraction
│   └── extract_features.py            <- step 3: extracts features via the masked group ICA map and saved mask from step 3
├── metadata                           <- contains important metadata
│   ├── healthy_subjects.txt           <- contains ids of healthy subjects used for ICA
│   ├── mask_ga_40.nii.gz              <- the brain mask used in step 3 of the pipeline
│   └── week40_T1w_215mm.nii.gz        <- the extended 40-week T1-weighted template for registration, downsampled to a spatial resolution of 2.15mm isotropic
└── registration                       <- contains all code necessary to register fMRI images to templates
    ├── register_multiple_fMRI.py      <- registers all images in a directory (optimized parallelism)
    ├── register_single_fMRI.py        <- registers one image to a specified template (optimized parallelism)
    ├── register_multiple_fMRI.sh/.py  <- registers all images in a directory, python for optimized parallelism
    └── register_single_fMRI.sh/.py    <- registers one image to a specified template, python for optimized parallelism
```

## Data

In the groupwise dHCP volumetric atlas exist 9 different gestational ages in total, from 36 to 44 weeks. We will choose 100 healthy subjects from this range. In this sense, we choose normally developing children, i.e. the ones with low risk of developmental delay according to their BSID-III and Q-CHAT scores. There are 725 subjects who have undertaken both Q-CHAT and BSID-III tests. In order to be seen with low risk of developmental delay, children need a BSID-III score higher than 85 regarding the cognitive, language and motor composite scores and a Q-CHAT score between or equal to 19 and 35.

We only use normally developing children's data since it might be more stable and less noisy (maybe less variability and fewer artifacts) and result in a more reliable set of features. Furthermore, such ICA process might help detecting deviations from the normally developing group.

431 from 725 children pass all tests. This means that 294 do not pass the test and are at risk of developmental delay/autism. 358 from these 431 children have fMRI data available. 348 children remain after removing all subjects with gestational ages outside the defined range.

![image](https://github.com/user-attachments/assets/2a69b6fc-5ab5-4a47-8653-b9a30c310ead)

The ids of these subjects may be found in **metadata/healthy_subjects/**. Some of these subjects have undergone multiple fMRI sessions - we have chosen to only use one fMRI session per subject for analysis.

### Justification for Q-CHAT Threshold

[One study](https://pubmed.ncbi.nlm.nih.gov/18240013/) suggests that
typically developing children receive a score between 19 and 35 while
children who later develop ASD receive a score between 38 and 66. This
is what we will use in our assumptions

### Justification for BSID-III Threshold

The [official paper](https://www.physio-pedia.com/Bayley_Scales_of_Infant_and_Toddler_Development)
of BSID-III states the assumption of a normal distribution,
with a mean of 100 and a standard deviation of 15. In fact, the official source
interprets it in 3 different classes, which are composed of:

* **greater than or equal to 85:** average
* **lower than 85:** risk of developmental delay
* **lower than 75:** moderate to severe mental impairment

In this assumption, almost all major publications trying to derive a machine
learning problem in this sense define it as a binary classification problem:

* **greater than or equal to 85:** low risk of developmental delay
* **lower than 85:** high risk of developmental delay

We can see that our data largely represents and supports these assumptions.

Papers using regression models:

* [BrainNetCNN: Convolutional neural networks for brain networks; towards predicting neurodevelopment](https://www.sciencedirect.com/science/article/pii/S1053811916305237)
* [Early prediction of cognitive deficits in very preterm infants using functional connectome data in an artificial neural network framework](https://www.sciencedirect.com/science/article/pii/S2213158218300329)

Papers focusing on binary classification:

* [Prediction of cognitive and motor outcome of preterm infants based on automatic quantitative descriptors from neonatal MR brain images](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5438406/)
* [A multi-task, multi-stage deep transfer learning model for early prediction of neurodevelopment in very preterm infants](https://www.nature.com/articles/s41598-020-71914-x)

## Setup

The setup works successfully for **Python 3.9.19**. **It did not work for newer Python versions!!!**

For this workflow, we use tools from **FSL 6.0.7.12**, namely *fslmerge*, *fslroi*, *fslval* and *MELODIC*. You can download FSL [here](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation). On Linux, make sure to add following files in your *bashrc* to set the necessary environment.

```
export FSLDIR="/home/<user>/fsl"
source $FSLDIR/etc/fslconf/fsl.sh
export PATH=$FSLDIR/bin:$PATH
```

Please make sure to register all images to the according T1-weighted image. If not yet registered, you can use the script *register_fMRI.sh* for this purpose.

The masks and T1 templates can be downloaded via the *download_templates.sh* and *download_masks.sh* scripts in the respective directories.

For image registration, we use tools from **ANTs 2.5.2**, namely *antsApplyTransforms*, *antsRegistrationSyNQuick.sh* and *ResampleImage*. To speed up
the registration process, we require **GNU parallel 20230822**.

## fMRI Image Registration

The fMRI images are required to be registered to the T1-weighted image. In oder to adhere to the spatial resolution of the original images (i.e. ~2.15mm isotropic),
we decided to downsample the T1-weighted template with an original spatial resolution of .5mm isotropic.

In accordance to the paper **The developing Human Connectome Project (dHCP) automated resting-state functional processing framework for newborn infants**, we have chosen to use the
extended 40-week T1-weighted template. In accordance, we take the mask of 40 weeks of gestational age from the paper **Unbiased construction of a temporally consistent morphological atlas of neonatal brain development**. 

## Workflow

1. generate group ICA map via MIGP - **run_group_ica.sh**
2. mask group ICA map and generate masks - **create_masks.py**
3. dual regression + connectivity map extraction for each subject - **extract_features.py**

![image](https://github.com/user-attachments/assets/d592721e-09dd-4ff9-bae2-32cab2750ea3)
