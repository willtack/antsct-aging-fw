# flywheel/antsct-aging-fw
Build context for a [Flywheel Gear](https://github.com/flywheel-io/gears/tree/master/spec) which runs a specialized version of the [ANTs](https://github.com/ANTsX/ANTs) Cortical Thickness pipeline for older patients. The container/gear employs a template for older individuals provided by Nick Tustison and a script for masking out or cropping neck voxels using [c3d](https://github.com/pyushkevich/c3d) provided by Paul Yushkevich and Sandhitsu Das.

[DockerHub](https://hub.docker.com/repository/docker/willtack/antsct-aging-fw)

# Base image 
[Github](https://github.com/ftdc-picsl/antsct-aging)

[DockerHub](https://hub.docker.com/repository/docker/cookpa/antsct-aging/general)

# Runtime options
#### Inputs:
- bids-filter-file: *A JSON file describing custom BIDS input filters using PyBIDS. Must contain 't1w' key (note lowercase 't'). See [example_filter.json](https://github.com/willtack/antsct-aging-fw/blob/master/example_filter.json). More info [here](https://fmriprep.readthedocs.io/en/latest/faq.html#how-do-I-select-only-certain-files-to-be-input-to-fMRIPrep).*
- t1w_anatomy: *T1-weighted anatomical NIfTI file. When provided this file will be used in place of any T1w images found in the current session's BIDS dataset.*
- mni-labels-\*: *One or more generic label images in the MNI152NLin2009cAsym space, to be warped to the subject space.*
- mni-cortical-labels-\*: *One or more cortical label images in the MNI152NLin2009cAsym space, to be propagated to the subject's cortical mask. Use this option if the label set contains only cortical labels.*

#### Configurations:
- BIDS-\* (subject, session, acq, run): *Specify the minimum set of BIDS fields for uniquely distinguishing exactly one T1w image in the BIDS dataset. Will be overridden by t1w_anatomy input or bids-filter-file input.*
- denoise: *Run denoising withing the ANTS Cortical Thickness pipeline. (Recommended).*
- num-threads: *Maximum number of CPU threads to use. Set to 0 to use as many threads as there are cores.*
- run-quick: *whether or not to use a quick registration step. (Not recommended).*
- trim-neck-mode: *three options related to neck trimming:*
    - mask: *sets neck region to 0*
    - crop: *crops neck region from image*
    - none: *uses the unaltered input image*

# Original algorithm:
antsCorticalThickness.sh [guide](https://github.com/ANTsX/ANTs/wiki/antsCorticalThickness-and-antsLongitudinalCorticalThickness-output) and [example](https://github.com/ntustison/antsCorticalThicknessExample).

Reference: [Tustison et al, 2014.](http://dx.doi.org/10.1016/j.neuroimage.2014.05.044)
