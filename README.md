# Grouped Independent Component Analysis (ICA) for the developing Human Connectome Project (dHCP)
The goal is to perform grouped Independent Component Analysis (ICA) to extract meaningful signals from neonatal brains via the developing Human Connectome Project (dHCP). These Independent Components are planned to be used as an input for SwiFUN, to extract task-related information from resting-state functional Magnetic Resonance Images (rsfMRI).

## Data

There exist 9 different gestational ages in total, from 36 to 44 weeks. Each gestational age needs to be handled separately, and we chose a maximum of 20 random samples of each gestational age. In this sense, we choose normally developing children, i.e. the ones with low risk of developmental delay according to their BSID-III and Q-CHAT scores. There are 725 subjects who have undertaken both Q-CHAT and BSID-III tests. In order to be seen with low risk of developmental delay, children need a BSID-III score higher than 85 regarding the cognitive, language and motor composite scores and a Q-CHAT score lower than or equal to 32.

We only use normally developing children's data since it might be more stable and less noisy (maybe less variability and fewer artifacts) and result in a more reliable set of features. Furthermore, such ICA process might help detecting deviations from the normally developing group.

408 from 725 children pass all tests. This means that 317 do not pass the test and are at risk of developmental delay/autism. 334 from these 408 children have fMRI data available. 321 children remain after removing all subjects with gestational ages outside the defined range.

![image](https://github.com/user-attachments/assets/7d69bb6f-e967-42b5-bf60-9dcd68d2afeb)

As we can see, there are unfortunately only 7 and 8 subjects available for gestational ages 36 and 37, respectively. In this case, we will use all data available to use for ICA.

The ids of these subjects may be found in **metadata/healthy_subjects/**. Some of these subjects have undergone multiple fMRI sessions - we have chosen to only use one fMRI session per subject for analysis.

For people with access to the ConnectomeLAB internal server, these files may be downloaded via the **download_healthy_subjects.py** script. Please make sure that everything is set up correctly in the ssh config file.

### Justification for Q-CHAT Threshold

Although [one study](https://pubmed.ncbi.nlm.nih.gov/18240013/) suggests that
typically developing children receive a score between 19 and 35 while
children who later develop ASD receive a score between 38 and 66, all major
literature derives a binary classification problem from this, such that:

* **lower or equal to 32:** low risk of being intellectually challenged
* **higher than 32:** high risk of being intellectually challenged

This is confirmed by the study [The Autism-Spectrum Quotient (AQ): Evidence from Asperger Syndrome/High-Functioning Autism, Males and Females, Scientists and Mathematicians](https://link.springer.com/article/10.1023/A:1005653411471).

Other literature citing above article to support their decision of following
a binary classification problem:

* [A machine learning autism classification based on logistic regression analysis](https://link.springer.com/article/10.1007/s13755-019-0073-5)
* [The Autism Spectrum Quotient: Children’s Version (AQ-Child)](https://link.springer.com/article/10.1007/s10803-007-0504-z)
* [Using Machine Learning Methods to Predict Autism Syndrome](http://paper.ijcsns.org/07_book/202004/20200427.pdf)
* [A Deep Neural Network-Based Model for Screening Autism Spectrum Disorder Using the Quantitative Checklist for Autism in Toddlers (QCHAT)](https://link.springer.com/article/10.1007/s10803-021-05141-2)

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

The fMRI images are required to be registered to their respective T1 images, i.e. to the T1-weighted template according to the gestational
age.

## Workflow

1. concatenate fMRI images along the temporal axis - **concat_fmri.sh**
2. generate group ICA map - **run_group_ica.sh**
3. mask group ICA map - **extract_features.py**
4. dual regression + connectivity map extraction for each subject - **extract_features.py**

This workflow is required for each gestational age.

```
FOR each gestational_age IN range(36, 45):
   CONCATENATE fMRI images FROM input_directory FOR current gestational_age INTO output_file
   GENERATE group ICA map FROM concatenated fMRI file FOR current gestational_age INTO output_directory
   APPLY brain_mask FOR current gestational_age TO group ICA map FOR current gestational_age INTO masked_output_file
   FOR each subject fMRI data IN subjects FOR current gestational_age:
      APPLY brain_mask FOR current gestational_age TO current subject
      PERFORM dual regression ON group ICA map FOR current gestational_age USING masked subject fMRI data
      EXTRACT connectivity map FROM masked subject fMRI data FOR current gestational_age INTO feature_output_directory
```

### Justification for Multiple Group ICA Maps and Masks

The greatest challenge for working with neonatal data is the great variability in brain size and structure happening in just a few
weeks. This is why [the official website](https://gin.g-node.org/BioMedIA/dhcp-volumetric-atlas-groupwise/src/master/mean) offers
a total of 9 masks for different gestational ages, i.e. between 36 and 44 weeks. Each brain is registered to a template according
to the gestational age. This becomes evident when looking into the affine matrices of the data.

![image](https://github.com/user-attachments/assets/baae8d81-8ce5-480f-8054-e5c2d196335e)

As seen in the picture, images with the same gestational age have the same affine matrices, while the data with different
gestational ages have different affine matrices. 

This alone would result in different (and incompatible) dimensionalities for dual regression and connectivity map extraction.
To address this issue, we need to generate and mask the group ICA maps with the data adhering to the gestational age of
the analyzed subjects. As a consequence, we will also work with **9 different ICA maps for each gestational age**.
