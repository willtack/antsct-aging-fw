# flywheel/ANTS-AGING-CT
Build context for a [Flywheel Gear](https://github.com/flywheel-io/gears/tree/master/spec) which runs a specialized case of the ANTs Cortical Thickness pipeline for older patients.

Repository for base Docker image: https://github.com/ftdc-picsl/antsct-aging

antsCorticalThickness.sh [guide](https://github.com/ANTsX/ANTs/wiki/antsCorticalThickness-and-antsLongitudinalCorticalThickness-output) and [example](https://github.com/ntustison/antsCorticalThicknessExample)

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

#### Citation for original algorithm:
Tustison NJ, Cook PA, Klein A, Song G, Das SR, Duda JT, Kandel BM, van Strien N, Stone JR, Gee JC, Avants BB. Large-scale evaluation of ANTs and FreeSurfer cortical thickness measurements. Neuroimage. 2014 Oct 1;99:166-79. doi: 10.1016/j.neuroimage.2014.05.044. Epub 2014 May 29. PMID: 24879923.
