"""
Created on Monday, Aug 7th, 2017

author: Clemens Dlaska and Tansel Baran Yasar

Contains the functions for retaining the spike information from the output of Klustakwik and performing further post-processing on spike trains.
"""

import numpy as np
import h5py
from utils.filtering import *
import pickle

def retain_cluster_info(probe,group,p):
    """
    This function extracts the spike info from the clu file output of Klustakwik that was run on a tetrode data and saves the spike times and waveforms for  a cluster in a pickle file.

    Inputs:
        group: index of channel groups (0 for the left-most and bottom-most, increasing upwards first in a shank and rightwards when the shank is complete)
        p: parameters dictionary for the recording session

    Outputs:
        Saves a pickle file in the same folder as the kwik file. The dictionary contains the following;
            P: spike info dictionary which consist of C sub-dictionaries where C is the number of clusters. Each sub-dictionary consists of the following:
                spike_times_cluster: times of the spikes that belong to this cluster
                waveforms: waveforms of the spikes that belong to this cluster
            p: Params dictionary from the rest of the pipeline
    """

    path_kwik_file = p['mainpath'] + '/analysis_files/probe_{:g}_group_{:g}/probe_{:g}_group_{:g}.kwik'.format(probe,group,probe,group) #path to the kwik file
    with h5py.File(path_kwik_file,'r') as hf:
        all_spiketimes = hf.get('channel_groups/0/spikes/time_samples') #accessing the spike times
        np_all_spiketimes = np.array(all_spiketimes) #converting the spike times to numpy array

    path_clu_file = p['mainpath'] + '/analysis_files/probe_{:g}_group_{:g}/probe_{:g}_group_{:g}.clu.0'.format(probe,group,probe,group) #accessing the file where the clustering information is stored
    np_clu_original = np.loadtxt(path_clu_file) #reading out the clustering information, which is an array with (number of spikes + 1) entries...
    nr_of_clusters = int(np_clu_original[0]) #... whose first entry is the number of clusters. As a result, we need to...
    np_clu = np_clu_original[1:] # ...separate the actual clustering information by excluding the first element.

    raw_data = np.fromfile(p['mainpath'] + '/analysis_files/probe_{:g}_group_{:g}/probe_{:g}_group_{:g}.dat'.format(probe,group,probe,group),dtype='int16') #reading out the raw data file
    num_samples = int(len(raw_data) / p['nr_of_electrodes_per_group'])
    raw_data = np.reshape(raw_data, (num_samples, p['nr_of_electrodes_per_group']))
    fil = bandpassFilter(rate=p['sample_rate'], low=p['low_cutoff'], high=p['high_cutoff'], order=3, axis = 0)
    raw_data_f = fil(raw_data)
    units = {}
    
    unit_indices = np.unique(np_clu)
    unit_indices = np.delete(unit_indices, [0,1])
    for cluster in unit_indices:
        spike_times_cluster_index = np.where(np_clu == cluster)
        spike_times_cluster = np_all_spiketimes[spike_times_cluster_index]
        num_spikes_in_cluster = len(spike_times_cluster)
        num_samples_per_waveform = p['samples_before'] + p['samples_after']
        waveforms = np.zeros((num_spikes_in_cluster,p['nr_of_electrodes_per_group'],num_samples_per_waveform))
        for spike in range(num_spikes_in_cluster):
            for trode in range(p['nr_of_electrodes_per_group']):
                for sample in range(num_samples_per_waveform):
                    waveforms[spike,trode,sample] = raw_data_f[(int(spike_times_cluster[spike])-p['samples_before']+sample), trode]

        unit = [0,0]
        unit[0] = spike_times_cluster
        unit[1] = waveforms
        units['unit{:g}'.format(cluster)] = unit

    path_pickle_file = p['mainpath'] + '/analysis_files/probe_{:g}_group_{:g}/probe_{:g}_group_{:g}_spikeinfo.pickle'.format(probe,group,probe,group)
    with open (path_pickle_file, 'wb') as f:
        pickle.dump({'units':units, 'params_dict':p} ,f)
