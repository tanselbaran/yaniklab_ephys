"""
Creation date: Tuesday, Aug 1st 2017

authors: Tansel Baran Yasar and Clemens Dlaska

Contains the functions that are used for creating the .prm and .prb files required for spike-sorting with Klustakwik, and running the Klustakwik on the tetrode or shank (for linear probes).
"""

import numpy as np
import os as os
import h5py
from itertools import combinations
import json
import pickle
from scipy import signal
from shutil import copyfile
from utils.filtering import *

### Klustakwik utilities for data analyzing ###

def create_prm_file(group,location):
    """
    This function creates the .prm file required by Klustakwik for the analysis of the data from the tetrode or shank of a linear probe with the group index s.

    Inputs:
        probe: Index of the probe, for recordings with multiple probes.
        s: Group index; shanks in the case of linear probes (0 for the left-most shank, looking at the electrode side), tetrodes in the case of tetrode organization (starting from the left and bottom-most tetrode first and increasing upwards column by column)
        p: Parameters dictionary containing the parameters and preferences related to spike sorting.
    """
    experiment = location.experiment
    probe = experiment.probe
    file_dir = location.dir + '/analysis_files/group_{:g}/group_{:g}.prm'.format(group,group)

    with open(file_dir, 'a') as text:
        print('experiment_name = \group_{:g}\''.format(group), file = text)
        print('prb_file = \'group_{:g}.prb\''.format(group), file = text)
        print('traces = dict(raw_data_files=[experiment_name + \'.dat\'],voltage_gain=10., sample_rate =' + str(experiment.sample_rate) + ', n_channels = ' + str(probe.nr_of_electrodes_per_group) + ', dtype = \'int16\')', file = text)

        print("spikedetekt = { \n 'filter_low' : %d., \n 'filter_high_factor': 0.95 * .5, \n 'filter_butter_order': 3, \n #Data chunks. \n 'chunk_size_seconds': 1., \n 'chunk_overlap_seconds': .015, \n #Threshold \n 'n_excerpts': 50, \n 'excerpt_size_seconds': 1., \n 'use_single_threshold': True, \n 'threshold_strong_std_factor': 4.5, \n 'threshold_weak_std_factor': 2., \n 'detect_spikes': 'negative', \n # Connected components. \n 'connected_component_join_size': 1, \n #Spike extractions. \n 'extract_s_before': %i, \n 'extract_s_after': %i, \n 'weight_power': 2, \n #Features. \n 'n_features_per_channel': 3, \n 'pca_n_waveforms_max': 10000}" % (experiment.low_pass_freq, experiment.spike_samples_before, experiment.spike_samples_after), file = text)

        print("klustakwik2 = { \n 'prior_point':1, \n 'mua_point':2, \n 'noise_point':1, \n 'points_for_cluster_mask':100, \n 'penalty_k':0.0, \n 'penalty_k_log_n':1.0, \n 'max_iterations':1000, \n 'num_starting_clusters':500, \n 'use_noise_cluster':True, \n 'use_mua_cluster':True, \n 'num_changed_threshold':0.05, \n 'full_step_every':1, \n 'split_first':20, \n 'split_every':40, \n 'max_possible_clusters':1000, \n 'dist_thresh':4, \n 'max_quick_step_candidates':100000000, \n 'max_quick_step_candidates_fraction':0.4, \n 'always_split_bimodal':False, \n 'subset_break_fraction':0.01, \n 'break_fraction':0.0, \n 'fast_split':False, \n 'consider_cluster_deletion':True, \n #'num_cpus':None, \n #'max_split_iterations':None \n}", file = text)

    text.close()

def create_prb_file(group,location):
    """
    This function creates the .prb file required by Klustakwik, which contains the electrode neighborhood and geometry information for the tetrode or shank of a linear probe with the group index s.

    Inputs:
        probe: Index of the probe, for recordings with multiple probes.
        s: Group index; shanks in the case of linear probes (0 for the left-most shank, looking at the electrode side), tetrodes in the case of tetrode organization (starting from the left and bottom-most tetrode first and increasing upwards column by column)
        p: Parameters dictionary containing the parameters and preferences related to spike sorting.
    """

    experiment = location.experiment
    probe = experiment.probe
    file_dir = location.dir + '/analysis_files/group_{:g}/group_{:g}.prb'.format(group,group)

    if probe.type == 'tetrode':
        tetrode = dict(channels = list(range(probe.nr_of_electrodes_per_group)), graph = list(combinations(range(probe.nr_of_electrodes_per_group),2)), geometry = {0: (0, 90), 1: (0, 60), 2: (0, 30), 3: (0, 0)})
        channel_groups = {0: tetrode}
        with open(file_dir, 'a') as text:
            print('channel_groups = {}'.format(channel_groups), file = text)
    elif probe.type == 'linear':
        copyfile('./prb_files/' + probe.name + '.prb', file_dir) #for the linear probes, just copy the probe file downloaded from the repository for the Neuronexus probe files
    elif probe.type == 'array':
        pass

def do_klusta(group,location):
    """
    This function runs the klustakwik for the tetrode or the shank of a linear probe.

    Inputs:
        probe: Index of the probe, for recordings with multiple probes.
        s: Group index; shanks in the case of linear probes (0 for the left-most shank, looking at the electrode side), tetrodes in the case of tetrode organization (starting from the left and bottom-most tetrode first and increasing upwards column by column)
        p: Parameters dictionary containing the parameters and preferences related to spike sorting.
    """

    file_dir = location.dir+ '/analysis_files/group_{:g}/'.format(group)
    os.chdir(file_dir)
    os.system('klusta group_{:g}.prm'.format(group))
