"""
Created on Tuesday, Aug 1st 2017

author: Tansel Baran Yasar

Contains the utilities for reading the data from different file formats created by Intan and Open Ephys
GUI softwares.
"""

import numpy as np
from utils.load_intan_rhd_format import *
import os
import utils.OpenEphys
import pickle

def read_amplifier_dat_file(filepath):
    """
    This function reads the data from a .dat file created by Intan software and returns as a numpy array.

    Inputs:
        filepath: The path to the .dat file to be read.

    Outputs:
        amplifier_file: numpy array containing the data from the .dat file (in uV)
    """

    with open(filepath, 'rb') as fid:
        raw_array = np.fromfile(fid, np.int16)
    amplifier_file = raw_array * 0.195 #converting from int16 to microvolts
    return amplifier_file

def read_time_dat_file(filepath, sample_rate):
    """
    This function reads the time array from a time.dat file created by Intan software for a recording session,
    and returns the time as a numpy array.

    Inputs:
        filepath: The path to the time.dat file to be read.
        sample_rate: Sampling rate for the recording of interest.

    Outputs:
        time_file: Numpy array containing the time array (in s)
    """

    with open(filepath, 'rb') as fid:
        raw_array = np.fromfile(fid, np.int32)
    time_file = raw_array / float(sample_rate) #converting from int32 to seconds
    return time_file

def read_group(probe,h,s,p):
    """
    This function reads the data for a given tetrode or the shank of a linear probe for a recording session and returns it as an array. It supports 'file_per_channel' ('dat') and 'file_per_recording' ('rhd') options of the Intan software and data from Open Ephys software ('cont'). It also saves this array in a .dat file in case spike sorting will be performed.

    Inputs:
        probe: Index specifying the probe (can be >0 in case of experiments with simultaneous recordings from multiple probes)
        h: Index specifying the height of the tetrode on the shank (starting from 0, bottom to top)
        s: Index specifying the shank (starting from 0, left to right)
        p: Parameters dictionary for the recording session to be analyzed

    Outputs:
        group_file: Numpy array containing the data from all electrodes in the tetrode or shank

    The function also generates a .dat file that contains the data for the tetrode in the format of ch0[t=0], ch1[t=0], ch2[t=0], ch3[t=0], ch0[t=1], ch1[t=1] etc.

    """
    id = probe * p['nr_of_electrodes'] + p['id'].astype(int) #Reading the channel id file from the parameters dictionary

    if p['fileformat'] == 'dat' or p['fileformat'] == 'cont':
        #If not exists, create a dictionary for the intermediate files for the channel group (shank or tetrode)
        if not os.path.exists(p['path'] + '/group_{:g}_{:g}'.format(probe,s)):
            os.mkdir(p['path'] + '/group_{:g}_{:g}'.format(probe,s))

        #Read the first electrode in the tetrode or shank to have a definite length for the group file array
        if p['fileformat'] == 'dat':
            #For the "channel per file" option of Intan
            info = read_data(p['path'] + '/info.rhd')
            electrode0_path = p['path'] + '/amp-' +  str(info['amplifier_channels'][int(id[h,s,0])]['native_channel_name']) + '.dat'
            electrode0 = read_amplifier_dat_file(electrode0_path)
        else:
            #For the OpenEphys files
            electrode0_path = p['path'] + '/100_CH' + str(id[h,s,0] + 1) + '.continuous'
            electrode0_dict = OpenEphys.load(electrode0_path)
            electrode0 = electrode0_dict['data']

        #Reading the rest of the electrodes in the tetrode or the shank
        ## For tetrodes
        if p['probe_type'] == 'tetrode':
            group_file = np.zeros((4, len(electrode0))) #Create  the array of the group file
            group_file[0] = electrode0
            for i in range(1,4):
                if p['fileformat'] == 'dat':
                    #For the "channel per file" option of Intan
                    electrode_path = p['path'] + '/amp-' + str(info['amplifier_channels'][int(id[h,s,i])]['native_channel_name']) + '.dat'
                    group_file[i] = read_amplifier_dat_file(electrode_path)
                else:
                    #For the OpenEphys files
                    electrode_path = p['path'] + '/100_CH' + str(id[h,s,i] + 1) + '.continuous'
                    electrode_dict = OpenEphys.load(electrode_path)
                    group_file[i] = electrode_dict['data']

        ## For linear probes
        elif p['probe_type'] == 'linear':
            group_file = np.zeros((p['nr_of_electrodes_per_shank'], len(electrode0)))
            group_file[0] = electrode0
    		#Reading out the data for each electrode and saving into the shank_file array
            for h in range(1, p['nr_of_electrodes_per_shank']):
                if p['fileformat'] == 'dat':
                    electrode_path = p['path'] + '/amp-' + str(info['amplifier_channels'][int(id[h,s])]['native_channel_name']) + '.dat'
                    group_file[h] = read_amplifier_dat_file(electrode_path)
                else:
                    electrode_path = p['path'] + '/100_CH' + str(id[h,s] + 1) + '.continuous'
                    electrode_dict = OpenEphys.load(electrode_path)
                    trace = electrode_dict['data']
                    group_file[h] = trace

    #Reading out the data for the "file per recording" option of Intan
    elif p['fileformat'] == 'rhd':
        #For tetrodes
        if p['probe_type'] == 'tetrode':
            group_file = np.zeros(4,0)
            for sample in range(len(p['rhd_file'])):
                data = read_data(p['path']+'/'+ p['rhd_file'][i])
                electrode_inds = [int(id[h,s,0]), int(id[h,s,1]), int(id[h,s,2]), int(id[h,s,3])]
                group_file = np.append(group_file, data['amplifier_data'][electrode_inds], 0)
        #For linear probes
        elif ['probe_type'] == 'linear':
            group_file = np.zeros((p['nr_of_electrodes_per_shank'],0))
            print(p['rhd_file'])
            for i in range(len(p['rhd_file'])):
                data = read_data(p['path']+'/'+ p['rhd_file'][i])
                electrode_inds = []
                for h in range(p['nr_of_electrodes_per_shank']):
                    electrode_inds = np.append(electrode_inds, id[h,s])
                electrode_inds = electrode_inds.astype(int)
                group_file = np.append(group_file, data['amplifier_data'][electrode_inds], 0)

    #Writing the data into the .dat file if spike sorting will be performed.
    if p['spikeSorting']:
        fid_write = open(p['mainpath'] +'/group_{:g}_group_{:g}.dat'.format(probe,s), 'w')
        shank_file_to_save = shank_file.transpose().round().astype('int16')
        shank_file_to_save.tofile(fid_write)

    return group_file
