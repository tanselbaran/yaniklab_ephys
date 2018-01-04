#this script was used only for tests 18/11/2017, Mozdas
#this part was written by Mehmet Ozdas for Mac (based on Baran Yasar's scripts)
#the only difference for Mac was adding  to dirs list (folder != '.DS_Store')


import numpy as np
import pickle
import os
import sys
import ipywidgets
import math
import shutil
from matplotlib.pyplot import *

def avg_eLFP_tw(MainPath, time_window, folder, probe_to_plot, shank_to_plot, trode_to_plot):
    main_path = MainPath  # with / at the end.
    tw = time_window # time window value
    probe = probe_to_plot
    shank = shank_to_plot
    trode = trode_to_plot
    p = pickle.load(open(main_path + '/' + folder + '/paramsDict.p', 'rb')) #Loading parameter dictionary
    len_time_window = tw * 60 * p['sample_rate']  # 30000 samples per second
    analyzed_path_for_folder = main_path + '/analyzed/' + folder
    evoked_LFP_timerange = np.arange(-p['evoked_pre'],p['evoked_post'],1/p['sample_rate'])  # 25
    peaks = []
    errs = []
    #lfp_averages=[]

    #4D array, 1st=probe number, 2nd=shank number= 3rd=electrode_no, num_window=peak numbers in graph

    analyzed_path_for_shank = analyzed_path_for_folder + '/probe_{:g}_group_{:g}/'.format(probe,shank)

    average_evoked_LFP_at_time_pdf_format = analyzed_path_for_shank + 'avg_eLFP_tw{:g}_pdf_format/'.format(tw)
    if not os.path.exists(average_evoked_LFP_at_time_pdf_format):
        os.mkdir(average_evoked_LFP_at_time_pdf_format)

    average_evoked_LFP_at_time_svg_format = analyzed_path_for_shank + 'avg_eLFP_tw{:g}_svg_format/'.format(tw)
    if not os.path.exists(average_evoked_LFP_at_time_svg_format):
        os.mkdir(average_evoked_LFP_at_time_svg_format)

    data_location = main_path + '/' + folder + ('/probe_{:g}_group_{:g}'.format(probe,shank)) + ('/probe_{:g}_group_{:g}_evoked.pickle'.format(probe,shank))
    evoked_data = pickle.load(open(data_location, 'rb'))
    evoked = evoked_data['evoked']

    stim_timestamps = evoked_data['stim_timestamps']
    num_window = int(np.max(stim_timestamps) / len_time_window)
    windows = np.arange(0,num_window,1)
    windows=windows*tw  # multiply by time window for the graph

    evoked_window_avgs = np.zeros((num_window, len(evoked[0]), len(evoked[0][0])))
    evoked_window_err = np.zeros((num_window, len(evoked[0]), len(evoked[0][0])))
    evoked_window_amps = np.zeros((p['probes'], p['shanks'], p['nr_of_electrodes_per_shank'], num_window))
    evoked_window_peak_errs = np.zeros((p['probes'], p['shanks'], p['nr_of_electrodes_per_shank'], num_window))
    lfp_averages = np.zeros((p['probes'],p['shanks'],p['nr_of_electrodes_per_shank'],num_window))

    for window in range(num_window):
        print("Time: {:g}".format(window))
        #Finding all the evoked data for which the time stamp falls in the window of interest
        evoked_window = evoked[np.all([stim_timestamps > window * len_time_window, stim_timestamps < (window + 1) * len_time_window], axis = 0)]
        evoked_window_avgs[window] = np.mean(evoked_window, 0) #  mean of evoked window
        evoked_window_std = np.std(evoked_window, 0) #Standard deviation of the data in the time window
        evoked_window_err[window] = evoked_window_std / math.sqrt(len(evoked_window)) # standard error of evoked window
        #Plotting and saving the figure for the average evoked LFP in this time window
        figure()
        plot(evoked_LFP_timerange, evoked_window_avgs[window][trode],'k-')
        xlabel('Time (ms)')# analyzed_path_for_folder
        ylabel('Peak voltage (uV)')
        ylim_min = np.floor(np.min(evoked) / 100) * 100
        ylim_max = np.ceil(np.max(evoked) / 100) * 100
        ylim(ylim_min, ylim_max)
        fill_between(evoked_LFP_timerange, evoked_window_avgs[window][trode]-evoked_window_err[window][trode], evoked_window_avgs[window][trode]+evoked_window_err[window][trode])
        print('plotting windows figures and saving')
        savefig(average_evoked_LFP_at_time_pdf_format +'average_evoked_LFP_at_time_{:g}_for_group_{:g}_electrode_{:g}'.format(window*tw, shank, trode)+'.pdf', format = 'pdf')
        savefig(average_evoked_LFP_at_time_svg_format +'average_evoked_LFP_at_time_{:g}_for_group_{:g}_electrode_{:g}'.format(window*tw, shank, trode)+'.svg', format = 'svg')
        close()
