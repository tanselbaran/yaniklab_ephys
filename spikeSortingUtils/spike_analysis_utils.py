"""
Created on Friday, Oct 6th, 2017

author: Tansel Baran Yasar

Contains the functions for analyzing spike trains.
"""

import numpy as np
from matplotlib.pyplot import *

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

def get_psth(unit, spike_trains, stim, bin_size):
    psth_range = np.arange(-50,200,bin_size)
    stim_inds = get_stim_inds(stim)
    evoked_train = np.zeros((len(stim_inds[rec]), (250*bin_size*global_params['sample_rate']/1000.)))
    for i, stim_ind in enumerate(stim_inds[rec]):
        evoked_train_rec[i] = spike_trains[unit][(stim_ind-50*global_params['sample_rate']/1000.):(stim_ind+200*global_params['sample_rate']/1000.)]

    evoked_psth = np.zeros((len(evoked_train_rec), 250*bin_size))
    for i in range(250):
        evoked_psth[:,i] = np.sum(evoked_train_rec[:,i*global_params['sample_rate']/1000.:(i+1)*global_params['sample_rate']/1000.], bin_size)
    return evoked_psth

def plot_psth(unit, evoked_psth, psth_range):
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
