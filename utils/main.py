"""
Uploaded to Github on Tuesday, Aug 1st 2017

authors: Tansel Baran Yasar and Clemens Dlaska

The main script for performing the spike sorting and LFP analysis on the recording sessions of interest.

Usage: Should be run through the IPython notebooks for spike sorting or LFP analysis.
"""

import sys
from load_intan_rhd_format import *
from reading_utils import *
from time import time
from data_processing_utils import *
from LFPutils.read_evoked_lfp import read_evoked_lfp
import pickle

def main(p):
    """
    This function is the main function for analysis that goes through the steps of the data analysis, based on the parameters and preferences provided in the parameters dictionary.

    Inputs:
        p: Dictionary of parameters that contains the parameters of recording and preferences regarding the particular mode of data analysis to be used. Usually created via the
        IPython notebook, "generate_params_dict.ipynb".
    """

    t0 = time()
    print('start')
    print('start reading out and analyzing trodes')

########Read out and Analysis################

#Tetrode
    #Iterating over probes, shanks and tetrodes
    if p['probe_type'] == 'tetrode':
        for probe in range(p['probes']):
            for h in range(p['max_nr_of_tetrodes_per_shank']):
                for s in range(p['shanks']):
                    print('########################  read data from tetrode {:g}{:g} ##############################'.format(h,s))
                    tetrode_file = read_tetrode(probe,h,s,p)
                    if p['spikesorting']:
                        print('################################### generate prm and prb file for tetrode {:g}{:g} ######################################################'.format(h,s))
                        create_tetrode_prm_file(probe,h,s,p)
                        create_tetrode_prb_file(probe,h,s,p)
                        print('################################## spikesorting, clustering of data in tetrode {:g}{:g} #################################################'.format(h,s))
                        do_klusta_for_tetrode(probe,h,s,p)
                    if p['LFP_analysis']:
                        print('############################# performing stimulus evoked LFP analysis for tetrode {:g}{:g} ##############################################'.format(h,s))
                        read_evoked_lfp(probe,[h,s],p,tetrode_file)

        t1 = time()
        print('Effort to read and analyze tetrodes: ', t1-t0)

#Linear
    #Iterating over probes and shanks
    elif p['probe_type'] == 'linear':
        for probe in range(p['probes']):
            for s in range(p['shanks']):
                print('########################  read data from probe {:g} shank {:g} ##############################'.format(probe,s))
                shank_file = read_linear(probe,s,p)
                if p['spikeSorting']:
                    print('################################### generate prm and prb file for probe {:g} shank {:g} ######################################################'.format(probe,s))
                    create_shank_prm_file(probe,s,p)
                    create_shank_prb_file(probe,s,p)
                    print('################################### spikesorting, clustering of probe {:g} shank {:g} data ###################################################'.format(probe,s))
                    do_klusta_for_shank(probe,s,p)
                if p['LFP_analysis']:
                    print('################################### performing stimulus evoked LFP analysis for probe {:g} shank {:g} ########################################'.format(probe,s))
                    read_evoked_lfp([probe,s],p,shank_file)

        t1 = time()
        print('Effort to read and analyze shanks: ', t1-t0)
