"""
Created on Friday, Oct 6th, 2017

author: Tansel Baran Yasar

Contains the functions for analyzing spike trains.
"""

import numpy as np
from matplotlib.pyplot import *

def firing_histogram(bin_size, spike_trains, sample_rate, end_times):
    """
    This function generates a histogram of the given spike trains with the given bin sizes.
    
    Inputs: 
        bin_size: The bin size for the histogram (in s)
        time: Array that contains the time of the recording (1x[total number of data samples])
        spike_trains: Spike train(s) to be analyzed. (Nx[total number of data samples] where N is the number of units for which the spike trains are analyzed)
        sample_rate: Sampling rate of the data (in Hz)
    
    Outputs: 
        hist: Array containing the histogram of the spiking activity (Nx[total number of bins in the histogram])
    """
    bin_size_inds = sample_rate * bin_size #converting bin size from seconds to samples
    hist = np.zeros((len(spike_trains), len(spike_trains[0])/bin_size_inds))
    for unit in range(len(hist)):
        for bin in range(len(hist[0])):
            hist[unit, bin] = np.sum(spike_trains[unit][int(i*bin_size_inds):int(min(time[-1]*global_params['sample_rate'], (i+1)*bin_size_inds))])
    
    return hist 

def get_firing_rate(spike_trains, end_inds, sample_rate):
    """
    This function calculates the average firing rates for the units for which the spike trains are given, for a given interval. 
    
    Inputs:
        spike_trains: Spike train(s) to be analyzed. (Nx[total number of data samples] where N is the number of units for which the spike trains are analyzed)
        sample_rate: Sampling rate of the data (in Hz)
        end_inds: The indices of the stim-spont or anesthesia level transitions in the recording trace 
    
    Outputs: 
        firing_rate: Array containing the firing rates for the units at each epoch (NxM array where N is the number of units and M is the number of epochs in the recording.
    """
    for unit in range(len(spike_trains)):
        for epoch in range(len(end_inds)-1):
            rec_time_len = (end_inds[epoch+1] - end_inds[epoch]) / sample_rate #calculating the length of the epoch
            firing_rate[unit][epoch] = np.sum(spike_trains[unit][int(end_inds[epoch]):int(end_inds[epoch+1])]) / rec_time_len #calculating the average firing rate of the unit in the epoch
    return firing_rate


def get_psth(spike_trains, stim, bounds, end_inds, bin_size, sample_rate):
    """
    This function generates the PSTHs of the spike trains of the units provided for the given epochs of stimulation and anesthesia levels. 
    
    Inputs: 
        spike_trains: Spike train(s) to be analyzed. (Nx[total number of data samples] where N is the number of units for which the spike trains are analyzed)
        stim: Array containing the digital input trace for the stimulus
        bounds: The milliseconds to be included in the PSTH prior and post the stimulus trigger
        end_inds: The indices of the stim-spont or anesthesia level transitions in the recording trace 
        bin_size: The bin size for the PSTH (in s)
        sample_rate: Sampling rate of the data (in Hz)
        
    Outputs: 
        PSTH: The PSTHs of the units for the given epochs in an array of size KxLxMxN  where K is the number of units, L is the number of epochs, M is the number of stimulus trigger events for that epoch and N is the number of samples in the range for one PSTH
    """
    
    psth_range = np.arange(bounds[0],bounds[1],bin_size)
    stim_inds = get_stim_inds(stim) #extracts stimulus timestamp indices
    evoked_train = np.zeros((len(stim_inds[rec]), ((bounds[1]-bounds[0])*bin_size*sample_rate/1000.)))
    for i, stim_ind in enumerate(stim_inds[rec]):
        evoked_train_rec[i] = spike_trains[unit][(stim_ind-50*global_params['sample_rate']/1000.):(stim_ind+200*global_params['sample_rate']/1000.)]

    evoked_psth = np.zeros((len(evoked_train_rec), 250*bin_size))
    for i in range(250):
        evoked_psth[:,i] = np.sum(evoked_train_rec[:,i*global_params['sample_rate']/1000.:(i+1)*global_params['sample_rate']/1000.], bin_size)
    return evoked_psth

def plot_firing_histogram(unit,       
    figure()
    plot(range(0,len(hist)*bin_size, bin_size), hist/bin_size, color = global_params['colors'][unit])
    for i in range(len(dirs)):
        axvline(end_inds[i+1]/global_params['sample_rate'], color = 'r', linestyle = 'dashed')
    xlabel('Time (s)')
    ylabel('Firing rate (Hz)')
    show()

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
