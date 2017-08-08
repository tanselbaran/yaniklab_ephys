"""
Uploaded to Github on Tuesday, Aug 1st, 2017

author: Tansel Baran Yasar

Contains the function for reading the stimulus-evoked LFP for a recording session.

Usage: through the main function in main.py script
"""

from utils.filtering import *
from utils.reading_utils import *
from utils.load_intan_rhd_format import *
from matplotlib.pyplot import *
from utils.OpenEphys import *
import pickle

def read_evoked_lfp(coords,p,data):
    """This function processes the data traces for the specified probe and shank in a recording session to obtain 
	the mean evoked LFP activity. It saves the evoked activity and the average evoked activity in a Pickle file. It 
	supports the data from 'file per channel' (dat) and 'file per recording' (rhd) options of Intan software and the 
	data recorded by Open Ephys software (cont).

        Inputs:
		coords: List including the coordinates of the shank or tetrode (either [height, shank] for tetrode configuration
			or [probe, shank] for linear configuration
            	p: Dictionary containing parameters (see main file)
		data: The numpy array that contains the data from either tetrode or shank in cases of tetrode or linear configurations 
			respectively

        Outputs:
            Saves the evoked LFP waveforms in a numpy array (number of trigger events x number of electrodes per shank x number 
		of samples in the evoked LFP window) and the time stamps of the stimulus trigger events in a pickle file saved in the folder
		for the particular probe and shank of the analysis. 
    """
    print('#### Low-pass and notch filtering the data ####') 
	
    if p['probe_type'] == 'tetrode':
        nr_of_electrodes = 4
        [h,s] = coords 
        save_file = p['path'] + '/tetrode_{:g}_{:g}_evoked.pickle'.format(h,s) 
         
    elif p['probe_type'] == 'linear':
        nr_of_electrodes = p['nr_of_electrodes_per_shank']
        [probe,s] = coords
        save_file = p['path'] + '/probe_{:g}_shank_{:g}'.format(probe,s) + '/probe_{:g}_shank_{:g}_evoked.pickle'.format(probe,s) 
        
    #Low pass filtering      
    filt = Filter(rate = p['sample_rate'], high = p['low_pass_freq'], order = 3)
    filtered = filt(data)
	
    #Notch filtering
    if p['notch_filt_freq'] != 0:
        notchFilt = notchFilter(rate = p['sample_rate'], low = p['notch_filt_freq']-5, high = p['notch_filt_freq']+5, order = 3)
        filtered = notchFilt(filtered)

    #filtered = np.transpose(filtered)
    
    #Reading the trigger timestamps (process varies depending on the file format

    if p['fileformat'] == 'dat':
        trigger_filepath =  p['path'] + '/board-DIN-01.dat' #In the case that the trigger is coming from the Digital Input 1 of the board
        with open(trigger_filepath, 'rb') as fid:
            trigger = np.fromfile(fid, np.int16)

        stim_timestamps = [] #numpy array that contains the stimulus timestamps
		#Saving the timestamps where digital input turns from 0 to 1
        for i in range(1,len(trigger)):
            if trigger[i-1] == 0 and trigger[i] == 1:
                stim_timestamps = np.append(stim_timestamps, i)

    elif p['fileformat'] == 'cont':
		#Reading the digital input from file
        trigger_filepath = p['path'] + '/all_channels.events'
        trigger_events = loadEvents(trigger_filepath)
        
        #Acquiring the timestamps of the ttl pulses
        timestamps = trigger_events['timestamps']
        eventId = trigger_events['eventId']
        eventType = trigger_events['eventType']
        channel = trigger_events['channel']
       
        timestamps_global = timestamps[eventType == 5]
        timestamps_ttl = []
        
        ttl_events = (eventType == 3)
        ttl_rise = (eventId == 1)
    
        for i in range(len(timestamps)):
            if (ttl_events[i]) and (ttl_rise[i]):
                timestamps_ttl = np.append(timestamps_ttl, timestamps[i])
                
        stim_timestamps = timestamps_ttl - timestamps_global[0]
    
    elif p['fileformat'] == 'rhd':
        trigger_all = []
        for file in range(len(p['rhd_file'])):
            data = read_data(p['path']+'/'+ p['rhd_file'][file])
            trigger = data['board_dig_in_data'][1] 
            trigger_all = np.append(trigger_all, trigger)
            
        stim_timestamps = []
        for i in range(1,len(trigger_all)):
            if trigger_all[i-1] == 0 and trigger_all[i] == 1:
                stim_timestamps = np.append(stim_timestamps, i)
    
    #Cutting the triggers that happen too close to the beginning or the end of the recording session
    stim_timestamps = stim_timestamps[(stim_timestamps > (p['cut_beginning']*p['sample_rate']))]
    stim_timestamps = stim_timestamps[(stim_timestamps < (len(trigger)-p['cut_end']*p['sample_rate']))]
    
	#Saving the evoked LFP waveforms in an array
    evoked = np.zeros((len(stim_timestamps), nr_of_electrodes, int(p['sample_rate']*(p['evoked_pre']+p['evoked_post']))))
    for i in range(len(stim_timestamps)):
        evoked[i,:,:] = filtered[:,int(stim_timestamps[i]-p['evoked_pre']*p['sample_rate']):int(stim_timestamps[i]+p['evoked_post']*p['sample_rate'])]

    #Save all evoked activity in a pickle file
    pickle.dump({'evoked':evoked, 'stim_timestamps':stim_timestamps}, open(save_file, 'wb'), protocol=-1)
