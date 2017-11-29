"""
Uploaded to Github on Tuesday, Aug 1st 2017

authors: Tansel Baran Yasar and Clemens Dlaska

The main script for performing the spike sorting and LFP analysis on the recording sessions of interest.

Usage: Should be run through the IPython notebooks for spike sorting or LFP analysis.
"""

import sys
from utils.load_intan_rhd_format import *
from utils.reading_utils import *
from spikeSortingUtils.klusta_preprocessing_utils import *
from LFPutils.read_evoked_lfp import read_evoked_lfp
from tqdm import tqdm
import pickle

def main(p):
    """
    This function is the main function for analysis that goes through the steps of the data analysis, based on the parameters and preferences provided in the parameters dictionary.

    Inputs:
        p: Dictionary of parameters that contains the parameters of recording and preferences regarding the particular mode of data analysis to be used. Usually created via the
        IPython notebook, "generate_params_dict.ipynb".
    """

    print('start reading out and analyzing trodes')

    #Getting the directory of the main path of the experiment for reference in future steps
    mycwd = os.getcwd()

    # Getting the number of channel groups in the probe (number of tetrodes for tetrode configuration and number of shanks for linear probe configuration)
    if p['probe_type'] == 'tetrode':
        nr_of_groups = p['nr_of_tetrodes']
    elif p['probe_type'] == 'linear':
        nr_of_groups = p['shanks']

########Read out and Analysis################
    for probe in range(p['probes']):
        for s in tqdm(range(nr_of_groups)):
            group_file = read_group(probe,s,p)
            if p['spikeSorting']:
                create_prm_file(probe,s,p)
                create_prb_file(probe,s,p)
                do_klusta(probe,s,p)
                os.chdir(mycwd)
            if p['LFP_analysis']:
                read_evoked_lfp(probe,s,p,group_file)
