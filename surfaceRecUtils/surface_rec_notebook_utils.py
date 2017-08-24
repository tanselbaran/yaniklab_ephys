import numpy as np
from matplotlib.pyplot import *
from utils.filtering import *
from utils.load_intan_rhd_format import *
from utils.reading_utils import *
from tqdm import tqdm
from LFPutils.read_evoked_lfp import *

def initialize_global_params(filter_type = 'bandpass', high_cutoff = 3000., low_cutoff = 300., sample_rate = 30000., pre = 0.8, post = 1.2, threshold_coeff = 5, artefact_limit = 20, cut_beginning = 1, cut_end = 1, evoked_pre = 0.05, evoked_post = 0.2, colors = ['xkcd:purple', 'xkcd:green', 'xkcd:pink', 'xkcd:brown', 'xkcd:red', 'xkcd:yellow', 'xkcd:bright green', 'xkcd:cyan', 'xkcd:black', 'xkcd:light orange'], spike_sorting = True, mode = 'Continuous'):
    spike_timerange = np.arange(-pre, post, (1000.0/sample_rate))

    global_params = {
        'sample_rate': sample_rate,
        'pre': pre,
        'post': post,
        'spike_timerange': spike_timerange,
        'filtertype': filter_type,
        'high_cutoff': high_cutoff,
        'low_cutoff': low_cutoff,
        'threshold_coeff': threshold_coeff,
        'artefact_limit': artefact_limit,
        'colors': colors,
        'spike_sorting': spike_sorting,
        'cut_beginning': cut_beginning,
        'cut_end': cut_end,
        'evoked_pre': evoked_pre,
        'evoked_post': evoked_post,
    }

    bandfilt = bandpassFilter(rate = sample_rate, high = high_cutoff, low = low_cutoff, order = 4)
    global_params['bandfilt'] = bandfilt

    return global_params

def read_location(dirs, channels, global_params):

    end_times = np.zeros(len(dirs))
    end_inds = np.zeros(len(dirs))
    data = np.zeros((len(channels), 0))
    waveforms = np.zeros((0,len(channels),60))
    peak_times = np.zeros(0)
    stim = np.zeros(0)
    current_end_time = 0
    time = np.zeros(0)

    for rec in tqdm(range(len(dirs))):
        mainfolder = dirs[rec]
        params = {}

        for key in global_params:
            params[key] = global_params[key]

        params['mainfolder'] = mainfolder
        params['rhd_path'] = mainfolder + 'info.rhd'
        params['time_path'] = mainfolder + 'time.dat'
        params['header'] = read_data(params['rhd_path'])
        params['time'] = read_time_dat_file(params['time_path'], global_params['sample_rate'])
        params['channels'] = channels
        params['stim_path'] = mainfolder + 'board-DIN-01.dat'
        params['stim'] = read_amplifier_dat_file(params['stim_path'])

        end_times[rec] = params['time'][-1]
        if rec == 0:
            time = np.append(time, params['time'])
        else:
            time = np.append(time, params['time'] + end_times[rec-1])

        data_electrode = np.zeros((len(params['channels']), len(params['time'])))
        for trode in range(len(params['channels'])):
            filepath = params['mainfolder'] + 'amp-' + params['header']['amplifier_channels'][params['channels'][trode]]['native_channel_name'] + '.dat'
            data_electrode[trode] = read_amplifier_dat_file(filepath)

        if global_params['spike_sorting'] == True:
            bandfilt = global_params['bandfilt']
            filtered_data_electrode = bandfilt(data_electrode)
            (waveforms_trode, peak_times_trode) = extract_waveforms(filtered_data_electrode, params)
            waveforms = np.append(waveforms, waveforms_trode, 0)
            peak_times = np.append(peak_times, peak_times_trode + current_end_time)

        data = np.append(data, data_electrode, 1)
        stim = np.append(stim, params['stim'])
        current_end_time = current_end_time + params['time'][-1]
        end_inds[rec] = np.sum((end_times*global_params['sample_rate'])[0:rec+1]) + rec
    end_inds = np.insert(end_inds,0,0)

    if global_params['spike_sorting'] == True:
        location_output = {'waveforms': waveforms, 'data':data, 'peak_times':peak_times, 'stim':stim, 'time':time, 'end_inds':end_inds}
    else:
        location_output = {'data':data, 'stim':stim, 'time':time, 'end_inds':end_inds}

    return location_output

def surface_evoked_LFP(location_output, begin, end, global_params, mode):
    if mode == 'evoked':
        stim_timestamps = extract_stim_timestamps_der(location_output['stim'])
    if mode == 'spont':
        stim_timestamps = np.arange(begin, end, global_params['sample_rate'])
    lowfilt = lowpassFilter(rate = global_params['sample_rate'], high = 300, order = 4)
    filtered_data = lowfilt(location_output['data'])
    evoked = read_evoked_lfp_from_stim_timestamps(filtered_data, begin, end, stim_timestamps, global_params)
    return evoked

def get_unit_indices(units, clusters):
    unit_indices = {}
    for unit in range(len(units)):
        unit_idx = np.zeros(0)
        for cluster in range(len(units[unit])):
            cluster_indices = np.where(clusters.labels_ == units[unit][cluster])
            unit_idx = np.append(unit_idx, cluster_indices)
        unit_idx = unit_idx.astype('int')
    unit_indices[unit] = unit_idx

    return unit_indices

def plot_unit_waveforms(unit, unit_indices, waveforms, global_params, plot_params):
    spikes_in_unit = better_waveforms[unit_indices[unit]]
    mean_spikes_in_unit = np.mean(spikes_in_unit, 0)
    fig, axs = subplots(plot_params['nrow'], plot_params['ncol'])
    channel = 0
    for i, ax in enumerate(fig.axes):
        ax.plot(global_params['spike_timerange'], mean_spikes_in_unit[channel])
        for spike in range(len(spikes_in_unit)):
            ax.plot(params['spike_timerange'], spikes_in_unit[spike,i], 'b', alpha=0.1)
        ax.set_ylim(plot_params['ylim'])
        ax.set_xlabel('Time (ms)')
        ax.set_ylabel('Voltage (uV)')
        channel = channel + 1
    show()

def get_unit_spike_times_and_trains(unit_indices, time, peak_times, global_params):
    spike_times = {}
    spike_trains = np.zeros((len(unit_indices), len(time)))

    for unit in range(len(unit_indices)):
        spike_times = peak_times[unit_indices[unit]]
        spike_times = np.asarray(spike_times * params['sample_rate'])
        spike_times = spike_times.astype(int)
        spike_times_all[unit] = np.sort(spike_times)
        spike_trains[unit][spike_times] = 1

    return spike_times, spike_trains

def firing_histogram(bin_size, unit, spike_trains, time, global_params, end_times):
    bin_size_inds = global_params['sample_rate'] * bin_size
    hist = np.zeros(len(time)/bin_size_inds)
    for i in range(len(hist)):
        hist[i] = np.sum(spike_trains[unit][int(i*bin_size_inds):int(min(time[-1]*global_params['sample_rate'], (i+1)*bin_size_inds))])

    figure()
    plot(range(0,len(hist)*bin_size, bin_size), hist/bin_size, color = global_params['colors'][unit])
    for i in range(len(dirs)):
        axvline(end_inds[i+1]/global_params['sample_rate'], color = 'r', linestyle = 'dashed')
    xlabel('Time (s)')
    ylabel('Firing rate (Hz)')
    show()

def get_firing_rate(unit, rec, spike_trains):
    rec_time_len = (end_inds[i+1] - end_inds[i]) / global_params['sample_rate']
    firing_rate = np.sum(spike_trains[unit][int(end_inds[i]):int(end_inds[i+1])]) / rec_time_len
    return firing_rate

def plot_psth(unit, rec, spike_trains, stim, bin_size):
    psth_range = np.arange(-50,200,bin_size)
    stim_inds = get_stim_inds(stim)
    evoked_train = np.zeros((len(stim_inds[rec]), (250*bin_size*global_params['sample_rate']/1000.)))
    for i, stim_ind in enumerate(stim_inds[rec]):
        evoked_train_rec[i] = spike_trains[unit][(stim_ind-50*global_params['sample_rate']/1000.):(stim_ind+200*global_params['sample_rate']/1000.)]

    evoked_psth = np.zeros((len(evoked_train_rec), 250*bin_size))
    for i in range(250):
        evoked_psth[:,i] = np.sum(evoked_train_rec[:,i*global_params['sample_rate']/1000.:(i+1)*global_params['sample_rate']/1000.], bin_size)

    figure()
    plot(psth_range, np.mean(evoked_psth, 0))
    axvline(0, color = 'r', linestyle = 'dashed')
    xlabel('Time (ms)')
    ylabel('Voltage (uV)')
    show()

def plot_spike_train(spike_trains, time, stim):
    fig, axs = subplots(2,1, sharex = 'all', figsize = (10,10))
    axs[0].plot(time, spike_trains[unit])
    axs[0].set_xlabel('Time (s)')
    axs[0].set_ylabel('Spike train')
    axs[1].plot(time, stim)
    show()

def plot_spikes_on_data(spike_times, data, stim, global_params):
    for i in range(len(global_params['channels'])):
        fig, axs = subplots(len(global_params['channels']), sharex = 'all', sharey = 'all', figsize = (10,10))
        axs[i].plot(time, data[i,:])
        for spike_ind in spike_times[unit]:
            axs[i].plot(np.arange(spike_ind-16, spike_ind+24) * (1/global_params['sample_rate']), data[i,spike_ind-16:spike_ind+24], color = global_params['colors'][unit])
        axs[i].set_xlabel('Time (s)')
        axs[i].set_ylabel('Voltage (uv)')
    show()
