"""
Created on Monday, Aug 7th, 2017

author: Clemens Dlaska and Tansel Baran Yasar

Contains the functions for retaining the spike information from the output of Klustakwik and performing further post-processing on spike trains.
"""

import numpy as np
import h5py

def retain_cluster_info_for_tetrode(h,s,p):
    """
    This function extracts the spike info from the clu file output of Klustakwik that was run on a tetrode data and saves the spike times and waveforms for  a cluster in a pickle file.
    
    Inputs: 
        h: height index of the tetrode (0 for the bottom-most tetrode of the shank, increasing as going up)
        s: shank index (0 for the left-most shank on the electrode side, increasing as going to right)
        p: parameters dictionary for the recording session
        
    Outputs: 
        Saves a pickle file in the same folder as the kwik file. The dictionary contains the following;
            P: spike info dictionary which consist of C sub-dictionaries where C is the number of clusters. Each sub-dictionary consists of the following:
                spike_times_cluster: times of the spikes that belong to this cluster
                waveforms: waveforms of the spikes that belong to this cluster    
    """
    path_kwik_file = p['path'] + '/tetrode_{:g}_{:g}'.format(h,s)+ '/tetrode_{:g}_{:g}.kwik'.format(h,s)
    with h5py.File(path_kwik_file,'r') as hf:
        all_spiketimes = hf.get('channel_groups/0/spikes/time_samples')
        np_all_spiketimes = np.array(all_spiketimes)

    path_clu_file = p['path'] + '/tetrode_{:g}_{:g}'.format(h,s)+ '/tetrode_{:g}_{:g}.clu.0'.format(h,s)
    np_clu_original = np.loadtxt(path_clu_file)
    nr_of_clusters = int(np_clu_original[0])
    np_clu = np_clu_original[1:]

    raw_data = np.fromfile(p['path'] + '/tetrode_{:g}_{:g}'.format(h,s) + '/tetrode_{:g}_{:g}.dat'.format(h,s) ,dtype='int16')
    fil = Filter(rate=p['sample_rate'], low=p['low_cutoff'], high=p['high_cutoff'], order=3)
    raw_data_f = fil(raw_data)

    for l in range(nr_of_clusters+1):
        spike_times_cluster_index = np.where(np_clu == l)
        spike_times_cluster = np_all_spiketimes[spike_times_cluster_index]
        N = len(spike_times_cluster)
        M = p['samples_per_spike']
        waveforms = np.zeros((N,4,M))
        for i in range(N):
            for j in range(4):
                for k in range(M):
                    waveforms[i,j,k] = raw_data_f[(int(spike_times_cluster[i])-p['samples_before']+k)*4+j]

        D = [0,0]
        D[0] = spike_times_cluster
        D[1] = waveforms
        P['c{:g}'.format(l)] = D

    path_pickle_file = p['path'] + '/tetrode_{:g}_{:g}'.format(h,s)+ '/tetrode_{:g}_{:g}_spikeinfo.pickle'.format(h,s)
    with open (path_pickle_file, 'wb') as f:
        pickle.dump({'P':P, 'p':p} ,f)


def retain_cluster_info_for_linear(s,p):
    """
    This function extracts the spike info from the clu file output of Klustakwik that was run on the data of a shank of a linear probe and saves the spike times and waveforms for  a cluster in a pickle file.
    
    Inputs: 
        s: shank index (0 for the left-most shank on the electrode side, increasing as going to right)
        p: parameters dictionary for the recording session
        
    Outputs: 
        Saves a pickle file in the same folder as the kwik file. The dictionary contains the following;
            P: spike info dictionary which consist of C sub-dictionaries where C is the number of clusters. Each sub-dictionary consists of the following:
                spike_times_cluster: times of the spikes that belong to this cluster
                waveforms: waveforms of the spikes that belong to this cluster    
    """
    path_kwik_file = p['path'] + '/probe_{:g}_shank_{:g}'.format(p,s)+ '/probe_{:g}_shank_{:g}.kwik'.format(p,s)
    with h5py.File(path_kwik_file,'r') as hf:
        all_spiketimes = hf.get('channel_groups/0/spikes/time_samples')
        np_all_spiketimes = np.array(all_spiketimes)

    path_clu_file = p['path'] + '/probe_{:g}_shank_{:g}'.format(p,s)+ '/probe_{:g}_shank_{:g}.clu.0'.format(p,s)
    np_clu_original = np.loadtxt(path_clu_file)
    nr_of_clusters = int(np_clu_original[0])
    np_clu = np_clu_original[1:]

    raw_data = np.fromfile(p['path'] + '/probe_{:g}_shank_{:g}'.format(p,s) + '/probe_{:g}_shank_{:g}.dat'.format(p,s) ,dtype='int16')
    fil = Filter(rate=p['sample_rate'], low=p['low_cutoff'], high=p['high_cutoff'], order=3)
    raw_data_f = fil(raw_data)

    for l in range(nr_of_clusters+1):
        spike_times_cluster_index = np.where(np_clu == l)
        spike_times_cluster = np_all_spiketimes[spike_times_cluster_index]
        N = len(spike_times_cluster)
        M = p['samples_per_spike']
        waveforms = np.zeros((N,p['nr_of_electrodes_per_shank'],M))
        for i in range(N):
            for j in range(p['nr_of_electrodes_per_shank']):
                for k in range(M):
                    waveforms[i,j,k] = raw_data_f[(int(spike_times_cluster[i])-p['samples_before']+k)*4+j]

        D = [0,0]
        D[0] = spike_times_cluster
        D[1] = waveforms
        P['c{:g}'.format(l)] = D

    path_pickle_file = p['path'] + '/probe_{:g}_shank_{:g}'.format(p,s)+ '/probe_{:g}_shank_{:g}_spikeinfo.pickle'.format(p,s)
    with open (path_pickle_file, 'wb') as f:
        pickle.dump({'P':P, 'p':p} ,f)
