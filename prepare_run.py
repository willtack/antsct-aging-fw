#!/usr/local/miniconda/bin/python
import sys
import logging
from pathlib import PosixPath
from fw_heudiconv.cli import export
import bids
import flywheel
import json
import os

# logging stuff
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('antsct-gear')
logger.info("=======: ANTs Cortical Thickness :=======")

# Gather variables that will be shared across functions
with flywheel.GearContext() as context:
    # Setup basic logging
    context.init_logging()
    # Log the configuration for this job
    # context.log_config()
    config = context.config
    analysis_id = context.destination['id']
    gear_output_dir = PosixPath(context.output_dir)
    antsct_script = gear_output_dir / "antsct_run.sh"
    output_root = gear_output_dir / analysis_id
    working_dir = PosixPath(str(output_root.resolve()) + "_work")
    bids_dir = output_root
    bids_root = output_root / 'bids_dataset'

    # Get relevant container objects
    fw = flywheel.Client(context.get_input('api_key')['key'])
    analysis_container = fw.get(analysis_id)
    project_container = fw.get(analysis_container.parents['project'])
    session_container = fw.get(analysis_container.parent['id'])
    subject_container = fw.get(session_container.parents['subject'])

    project_label = project_container.label

    # inputs
    manual_t1 = context.get_input('t1_anatomy')
    manual_t1_path_config = None if manual_t1 is None else \
        PosixPath(context.get_input_path('t1_anatomy'))

    bids_filter = context.get_input('bids-filter-file')
    bids_filter_path = None if bids_filter is None else \
        PosixPath(context.get_input_path('bids-filter-file'))

    # replace any spaces in the string
    if ' ' in str(manual_t1_path_config):
        manual_t1_path = PosixPath(str(manual_t1_path_config).replace(' ', '_'))
        # rename the actual file
        os.rename(manual_t1_path_config, manual_t1_path)
    else:
        manual_t1_path = manual_t1_path_config

    mni_cort_labels_1 = context.get_input('mni-cortical-labels-1')
    mni_cort_labels_1_path = None if mni_cort_labels_1 is None else \
        PosixPath(context.get_input_path('mni-cortical-labels-1'))

    mni_cort_labels_2 = context.get_input('mni-cortical-labels-2')
    mni_cort_labels_2_path = None if mni_cort_labels_2 is None else \
        PosixPath(context.get_input_path('mni-cortical-labels-2'))

    mni_cort_labels_3 = context.get_input('mni-cortical-labels-3')
    mni_cort_labels_3_path = None if mni_cort_labels_3 is None else \
        PosixPath(context.get_input_path('mni-cortical-labels-3'))

    # create space separated list (str)
    mni_cort_labels_path_list = [mni_cort_labels_1_path, mni_cort_labels_2_path, mni_cort_labels_3_path]
    # use list comprehension to remove None values
    mni_cort_labels_path_list = [str(i) for i in mni_cort_labels_path_list if i]
    mni_cort_labels_paths_str = " ".join(mni_cort_labels_path_list)

    mni_labels_1 = context.get_input('mni-labels-1')
    mni_labels_1_path = None if mni_labels_1 is None else \
        PosixPath(context.get_input_path('mni-labels-1'))

    mni_labels_2 = context.get_input('mni-labels-2')
    mni_labels_2_path = None if mni_labels_2 is None else \
        PosixPath(context.get_input_path('mni-labels-2'))

    mni_labels_3 = context.get_input('mni-labels-3')
    mni_labels_3_path = None if mni_labels_3 is None else \
        PosixPath(context.get_input_path('mni-labels-3'))

    # create space separated list (str)
    mni_labels_path_list = [mni_labels_1_path, mni_labels_2_path, mni_labels_3_path]
    # use list comprehension to remove None values
    mni_labels_path_list = [str(i) for i in mni_labels_path_list if i]
    mni_labels_paths_str = " ".join(mni_labels_path_list)

    # Get T1 image
    logger.info("manual_t1: %s" % manual_t1)
    logger.info("manual_t1_path: %s" % manual_t1_path)

    # configs, use int() to translate the booleans to 0 or 1
    # output_prefix = config.get('output-file-root')
    denoise = int(config.get('denoise'))
    num_threads = config.get('num-threads')
    run_quick = int(config.get('run-quick'))
    trim_neck_mode = config.get('trim-neck-mode')
    bids_acq = config.get('BIDS-acq')
    bids_run = config.get('BIDS-run')
    bids_sub = config.get('BIDS-subject')
    bids_ses = config.get('BIDS-session')


def write_command(anat_input, prefix):

    """Create a command script."""
    with flywheel.GearContext() as context:
        cmd = ['/opt/scripts/runAntsCT_nonBIDS.pl',
               '--anatomical-image {}'.format(anat_input),
               '--output-dir {}'.format(gear_output_dir),
               '--output-file-root {}'.format(prefix),
               '--denoise {}'.format(denoise),
               '--num-threads {}'.format(num_threads),
               '--run-quick {}'.format(run_quick),
               '--trim-neck-mode {}'.format(trim_neck_mode)
               ]
        if mni_cort_labels_paths_str:
            cmd.append('--mni-cortical-labels {}'.format(mni_cort_labels_paths_str))

        if mni_labels_paths_str:
            cmd.append('--mni-labels {}'.format(mni_labels_paths_str))

    logger.info(' '.join(cmd))
    with antsct_script.open('w') as f:
        f.write(' '.join(cmd))

    return antsct_script.exists()


def fw_heudiconv_download():
    """Use fw-heudiconv to download BIDS data."""
    subjects = [subject_container.label]
    sessions = [session_container.label]

    # Use manually specified T1 if it exists
    if manual_t1 is not None:
        anat_input = manual_t1_path
        subject_label = subject_container.label.replace('_', 'x').replace(' ', 'x')
        session_label = session_container.label.replace('_', 'x').replace(' ', 'x')
        prefix = 'sub-{}_ses-{}_'.format(subject_label, session_label)
        return True, anat_input, prefix

    # Do the download!
    bids_root.parent.mkdir(parents=True, exist_ok=True)
    downloads = export.gather_bids(fw, project_label, subjects, sessions)
    export.download_bids(fw, downloads, str(bids_dir.resolve()), dry_run=False, folders_to_download=['anat'])

    bids.config.set_option('extension_initial_dot', True)  # suppress warning
    layout = bids.BIDSLayout(bids_root)
    filters = {}

    if bids_filter_path:
        logger.info("Using {} as BIDS filter.".format(bids_filter_path))
        with open(bids_filter_path) as f:
            data = json.load(f)
        try:
            filters = data["t1w"]
        except KeyError as ke:
            print(ke)
            logger.warning("Could not find 't1w' field in json.")
            logger.info("BIDS filter file not formatted correctly.")
            return False
    else:
        if bids_sub:
            filters["subject"] = [bids_sub]
        else:
            filters["subject"] = subjects
        if bids_ses:
            filters["session"] = [bids_ses]
        else:
            filters["session"] = sessions

        if bids_acq:
            filters["acquisition"] = bids_acq

        if bids_run:
            filters["run"] = bids_run

    anat_list = layout.get(return_type='file', suffix='T1w', extension=['.nii', '.nii.gz'], **filters)

    # if there are multiple files or no files, error out
    # otherwise just use the one
    if len(anat_list) > 1:
        logger.warning("Multiple anatomical files found in %s. If you want to process multiple images, use the longitudinal gear.",
                       bids_root)
        return False
    elif not len(anat_list) or len(anat_list) == 0:
        logger.warning("No anatomical files found in %s", bids_root)
        return False
    else:
        anat_input = anat_list[0]

    logger.info("Using {} as input anatomical image.".format(anat_input))

    # Generate prefix from bids layout
    basename = os.path.basename(anat_input).split('.')[0]
    prefix = basename.replace('_T1w', '') + '_'

    return True, anat_input, prefix


def main():
    download_ok, anat_input, prefix = fw_heudiconv_download()
    sys.stdout.flush()
    sys.stderr.flush()
    if not download_ok:
        logger.warning("Critical error while trying to download BIDS data.")
        return 1

    command_ok = write_command(anat_input, prefix)
    sys.stdout.flush()
    sys.stderr.flush()
    if not command_ok:
        logger.warning("Critical error while trying to write ANTs-CT command.")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
