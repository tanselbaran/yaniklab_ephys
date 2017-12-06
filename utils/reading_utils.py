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

def read_group(probe,s,p):
    """
    This function reads the data for a given tetrode or the shank of a linear probe for a recording session and returns it as an array. It supports 'file_per_channel' ('dat') and 'file_per_recording' ('rhd') options of the Intan software and data from Open Ephys software ('cont'). It also saves this array in a .dat file in case spike sorting will be performed.

    Inputs:
        probe: Index specifying the probe (can be >0 in case of experiments with simultaneous recordings from multiple probes)
        s: Index specifying the shank (starting from 0, left to right)
        p: Parameters dictionary for the recording session to be analyzed

    Outputs:
        group_file: Numpy array containing the data from all electrodes in the tetrode or shank

    The function also generates a .dat file that contains the data for the tetrode in the format of ch0[t=0], ch1[t=0], ch2[t=0], ch3[t=0], ch0[t=1], ch1[t=1] etc.

    """
    id = probe * p['nr_of_electrodes'] + p['id'].astype(int) #Reading the channel id file from the parameters dictionary
    #If not exists, create a folder where the analysis files for the entire experiment would be stored for klusta purposes
    if not os.path.exists(p['mainpath'] + '/analysis_files'):
        os.mkdir(p['mainpath'] + '/analysis_files')

    if p['fileformat'] == 'dat' or p['fileformat'] == 'cont':
        #If not exists, create a dictionary for the intermediate files for the channel group (shank or tetrode)
        if not os.path.exists(p['path'] + '/probe_{:g}_group_{:g}'.format(probe,s)):
            os.mkdir(p['path'] + '/probe_{:g}_group_{:g}'.format(probe,s))

        #Read the first electrode in the tetrode or shank to have a definite length for the group file array
        if p['fileformat'] == 'dat':
            #For the "channel per file" option of Intan
            info = read_data(p['path'] + '/info.rhd')
            electrode0_path = p['path'] + '/amp-' +  str(info['amplifier_channels'][int(id[0,s])]['native_channel_name']) + '.dat'
            electrode0 = read_amplifier_dat_file(electrode0_path)
        else:
            #For the OpenEphys files
            electrode0_path = p['path'] + '/100_CH' + str(id[0,s] + 1) + '.continuous'
            electrode0_dict = OpenEphys.load(electrode0_path)
            electrode0 = electrode0_dict['data']

        #Reading the rest of the electrodes in the tetrode or the shank

        group_file = np.zeros((p['nr_of_electrodes_per_group'], len(electrode0))) #Create  the array of the group file
        group_file[0] = electrode0
        for trode in range(1,p['nr_of_electrodes_per_group']):
            if p['fileformat'] == 'dat':
                #For the "channel per file" option of Intan
                electrode_path = p['path'] + '/amp-' + str(info['amplifier_channels'][int(id[trode,s])]['native_channel_name']) + '.dat'
                group_file[trode] = read_amplifier_dat_file(electrode_path)
            else:
                #For the OpenEphys files
                electrode_path = p['path'] + '/100_CH' + str(id[trode,s] + 1) + '.continuous'
                electrode_dict = OpenEphys.load(electrode_path)
                group_file[trode] = electrode_dict['data']

    #Reading out the data for the "file per recording" option of Intan
    elif p['fileformat'] == 'rhd':
        group_file = np.zeros((p['nr_of_electrodes_per_group'],0))
        for sample in range(len(p['rhd_file'])):
            data = read_data(p['path']+'/'+ p['rhd_file'][sample])
            electrode_inds = []
            for trode in range(p['nr_of_electrodes_per_group']):
                electrode_inds = np.append(electrode_inds, id[trode,s])
            electrode_inds = electrode_inds.astype(int)
            group_file = np.append(group_file, data['amplifier_data'][electrode_inds], 0)

    #Writing the data into the .dat file if spike sorting will be performed.
    if p['spikeSorting']:
        if not os.path.exists(p['mainpath'] + '/analysis_files/probe_{:g}_group_{:g}'.format(probe,s)):
            os.mkdir(p['mainpath'] + '/analysis_files/probe_{:g}_group_{:g}'.format(probe,s))
        if p['order'] == 0:
            fid_write = open(p['mainpath'] +'/analysis_files/probe_{:g}_group_{:g}/probe_{:g}_group_{:g}.dat'.format(probe,s,probe,s), 'w')
        else:
            fid_write = open(p['mainpath'] +'/analysis_files/probe_{:g}_group_{:g}/probe_{:g}_group_{:g}.dat'.format(probe,s,probe,s), 'a')
        group_file_to_save = group_file.transpose().round().astype('int16')
        group_file_to_save.tofile(fid_write)
        fid_write.close()

    return group_file
