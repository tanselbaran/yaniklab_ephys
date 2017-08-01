import numpy as np
import os as os
import h5py
from itertools import combinations
import json
import pickle
from scipy import signal
from shutil import copyfile


def create_tetrode_prm_file(h,s,p):
   file_dir = p['path'] + '/tetrode_{:g}_{:g}'.format(h,s)+'/tetrode_{:g}_{:g}.prm'.format(h,s)
   with open(file_dir, 'a') as text:
        print('experiment_name = \'tetrode_{:g}_{:g}\''.format(h,s), file = text)
        print('prb_file = \'tetrode_{:g}_{:g}.prb\''.format(h,s), file = text)
        print('traces = dict(raw_data_files=[experiment_name + \'.dat\'],voltage_gain=10., sample_rate =' + str(p['sample_rate']) + ', n_channels = 4, dtype = \'int16\')', file = text)
        print('spikedetekt = dict()', file = text)
        print('klustakwik2 = dict(num_starting_clusters=100,)', file = text)       


def create_tetrode_prb_file(h,s,p):
    file_dir = p['path'] + '/tetrode_{:g}_{:g}'.format(h,s)+'/tetrode_{:g}_{:g}.prb'.format(h,s)
    tetrode = dict(channels = list(range(4)), graph = list(combinations(range(4),2)), geometry = {0: (0, 90), 1: (0, 60), 2: (0, 30), 3: (0, 0)})
    channel_groups = {0: tetrode}
    with open(file_dir, 'a') as text:
        print('channel_groups = {}'.format(channel_groups), file = text)    
        
def do_klusta(h,s,p):
    file_dir = p['path'] + '/tetrode_{:g}_{:g}'.format(h,s)
    os.chdir(file_dir) 
    os.system('klusta tetrode_{:g}_{:g}.prm'.format(h,s))

def create_shank_prm_file(probe,s,p):
    file_dir = p['path'] + '/probe_{:g}_shank_{:g}'.format(probe,s) + '/probe_{:g}_shank_{:g}.prm'.format(probe,s)
    if os.path.exists(file_dir):
        os.remove(file_dir)
    with open(file_dir, 'a') as text:
        print('experiment_name = \'probe_{:g}_shank_{:g}\''.format(probe,s), file = text)
        print('prb_file = \'probe_{:g}_shank_{:g}.prb\''.format(probe,s), file = text)
        print('traces = dict(raw_data_files=[experiment_name + \'.dat\'],voltage_gain=10., sample_rate =' + str(p['sample_rate']) + ', n_channels = ' + str(p['nr_of_electrodes']) + ', dtype = \'int16\')', file = text)
        print('spikedetekt = dict()', file = text)
        print('klustakwik2 = dict(num_starting_clusters=100,)', file = text)  
    text.close()
        
def create_shank_prb_file(probe,s,p):
    file_dir = p['path'] + '/probe_{:g}_shank_{:g}'.format(probe,s) + '/probe_{:g}_shank_{:g}.prb'.format(probe,s)
    copyfile('/home/baran/Desktop/tetrode_pipeline/prb_files/' + p['probe_name'] + '.prb', file_dir)
    
def do_klusta_for_shank(probe,s,p):
    file_dir = p['path'] + '/probe_{:g}_shank_{:g}'.format(probe,s)
    os.chdir(file_dir) 
    os.system('klusta probe_{:g}_shank_{:g}.prm'.format(probe,s))
    
def timestamps_isi_waveforms(h,s,c,p):
    path_kwik_file = p['path'] + '/tetrode_{:g}_{:g}'.format(h,s)+ '/tetrode_{:g}_{:g}.kwik'.format(h,s)
    with h5py.File(path_kwik_file,'r') as hf:
        all_spiketimes = hf.get('channel_groups/0/spikes/time_samples')
        np_all_spiketimes = np.array(all_spiketimes)
        
    path_clu_file = p['path'] + '/tetrode_{:g}_{:g}'.format(h,s)+ '/tetrode_{:g}_{:g}.clu.0'.format(h,s)
    np_clu_original = np.loadtxt(path_clu_file)
    np_clu = np_clu_original[1:]
    spike_times_cluster_index = np.where(np_clu == c)
    spike_times_cluster = np_all_spiketimes[spike_times_cluster_index]
    
    isi = [spike_times_cluster[i+1]-spike_times_cluster[i] for i in range(len(spike_times_cluster)-1)]
    
    raw_data = np.fromfile(p['path'] + '/tetrode_{:g}_{:g}'.format(h,s) + '/tetrode_{:g}_{:g}.dat'.format(h,s) ,dtype='int16')
    fil = Filter(rate=20000., low=500., high=6000., order=3) 
    raw_data_f = fil(raw_data)
    N = len(spike_times_cluster)
    M = p['samples_per_spike']
    waveforms = np.zeros((N,4,M))
    waveforms_f = np.zeros((N,4,M))
    for i in range(N):
        for j in range(4):
            for k in range(M):
                waveforms[i,j,k] = raw_data[(int(spike_times_cluster[i])-p['samples_before']+k)*4+j]
                waveforms_f[i,j,k] = raw_data_f[(int(spike_times_cluster[i])-p['samples_before']+k)*4+j]
        
    D = [0,0,0,0]
    D[0] = spike_times_cluster
    D[1] = isi
    D[2] = waveforms
    D[3] = waveforms_f
    

    
    path_pickle_file = p['path'] + '/tetrode_{:g}_{:g}'.format(h,s)+ '/tetrode_{:g}_{:g}_c{:g}_timestamps_isi_waveform.pickle'.format(h,s,c)
    with open (path_pickle_file, 'wb') as f:
        pickle.dump(D,f)
        

def generate_spikeinfo_pickle(h,s,p):
    path_kwik_file = p['path'] + '/tetrode_{:g}_{:g}'.format(h,s)+ '/tetrode_{:g}_{:g}.kwik'.format(h,s)
    with h5py.File(path_kwik_file,'r') as hf:
        all_spiketimes = hf.get('channel_groups/0/spikes/time_samples')
        np_all_spiketimes = np.array(all_spiketimes)
        
    path_clu_file = p['path'] + '/tetrode_{:g}_{:g}'.format(h,s)+ '/tetrode_{:g}_{:g}.clu.0'.format(h,s)
    np_clu_original = np.loadtxt(path_clu_file)
    nr_of_clusters = int(np_clu_original[0])
    np_clu = np_clu_original[1:]
    
    raw_data = np.fromfile(p['path'] + '/tetrode_{:g}_{:g}'.format(h,s) + '/tetrode_{:g}_{:g}.dat'.format(h,s) ,dtype='int16')
    fil = Filter(rate=20000., low=500., high=6000., order=3) 
    raw_data_f = fil(raw_data)
    
    P={}
    
    for l in range(nr_of_clusters+1):
        spike_times_cluster_index = np.where(np_clu == l)
        spike_times_cluster = np_all_spiketimes[spike_times_cluster_index]
        isi = [spike_times_cluster[i+1]-spike_times_cluster[i] for i in range(len(spike_times_cluster)-1)]
        N = len(spike_times_cluster)
        M = p['samples_per_spike']
        waveforms = np.zeros((N,4,M))
        waveforms_f = np.zeros((N,4,M))
        for i in range(N):
            for j in range(4):
                for k in range(M):
                    waveforms[i,j,k] = raw_data[(int(spike_times_cluster[i])-p['samples_before']+k)*4+j]
                    waveforms_f[i,j,k] = raw_data_f[(int(spike_times_cluster[i])-p['samples_before']+k)*4+j]
            
        D = [0,0,0,0]
        D[0] = spike_times_cluster
        D[1] = isi
        D[2] = waveforms
        D[3] = waveforms_f
        
        P['c{:g}'.format(l)] = D
        
        data = {'raw_data':raw_data, 'p':p}
    path_pickle_file = p['path'] + '/tetrode_{:g}_{:g}'.format(h,s)+ '/tetrode_{:g}_{:g}_spikeinfo.pickle'.format(h,s)
    with open (path_pickle_file, 'wb') as f:
        pickle.dump({'P':P, 'data':data} ,f)
     
    
       
