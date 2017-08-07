import numpy as np
import h5py

def retain_cluster_info_for_tetrode(h,s,p):
    path_kwik_file = p['path'] + '/tetrode_{:g}_{:g}'.format(h,s)+ '/tetrode_{:g}_{:g}.kwik'.format(h,s)
    with h5py.File(path_kwik_file,'r') as hf:
        all_spiketimes = hf.get('channel_groups/0/spikes/time_samples')
        np_all_spiketimes = np.array(all_spiketimes)

    path_clu_file = p['path'] + '/tetrode_{:g}_{:g}'.format(h,s)+ '/tetrode_{:g}_{:g}.clu.0'.format(h,s)
    np_clu_original = np.loadtxt(path_clu_file)
    nr_of_clusters = int(np_clu_original[0])
    np_clu = np_clu_original[1:]

    raw_data = np.fromfile(p['path'] + '/tetrode_{:g}_{:g}'.format(h,s) + '/tetrode_{:g}_{:g}.dat'.format(h,s) ,dtype='int16')
    fil = Filter(rate=p['sample_rate']., low=300., high=3000., order=3)
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
        pickle.dump({'P':P, 'data':raw_data, 'p':p} ,f)
