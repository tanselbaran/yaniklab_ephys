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

def analyze_time_windows(MainPath, time_window):
    main_path=MainPath  # with / at the end.
    tw=time_window # time window value

    #########################
    dirs=os.listdir(main_path)

    for folder in (folder for folder in dirs if ((folder != 'log.txt') and (folder != 'notes.docx') and (folder != 'other') and (folder != '.DS_Store') and (folder != 'analyzed') and (folder != 'analysis_files'))):
        print(folder)
        p = pickle.load(open(main_path + '/' + folder + '/paramsDict.p', 'rb')) #Loading parameter dictionary
        len_time_window = tw * 60 * p['sample_rate']  # 30000 samples per second
        analyzed_path_for_folder = main_path + '/analyzed/' + folder
        evoked_LFP_timerange = np.arange(-p['evoked_pre'],p['evoked_post'],1/p['sample_rate'])  # 25
        peaks = []
        errs = []
        #lfp_averages=[]

        #4D array, 1st=probe number, 2nd=shank number= 3rd=electrode_no, num_window=peak numbers in graph
        for probe in range(p['probes']):
            for shank in range(p['shanks']):

                analyzed_path_for_shank = analyzed_path_for_folder + '/probe_{:g}_group_{:g}/'.format(probe,shank)

                tw_pdf_format = analyzed_path_for_shank + 'tw{:g}_pdf_format/'.format(tw) # for saving images in pdf format
                if not os.path.exists(tw_pdf_format): # if not, create folder
                    os.mkdir(tw_pdf_format)

                tw_svg_format = analyzed_path_for_shank + 'tw{:g}_svg_format/'.format(tw)
                if not os.path.exists(tw_svg_format): # create  a new fiel and store images here
                    os.mkdir(tw_svg_format)

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

                     for trode in range(p['nr_of_electrodes_per_shank']):
                        evoked_window_amps[probe][shank][trode][window] = np.min(evoked_window_avgs[window][trode])
                        min_error = evoked_window_err[window][probe][np.where(evoked_window_avgs[window][trode] == np.min(evoked_window_avgs[window][trode]))]
                        max_error = evoked_window_err[window][probe][np.where(evoked_window_avgs[window][trode] == np.max(evoked_window_avgs[window][trode]))]
                        if len(min_error) == 1:
                            evoked_window_peak_errs[probe][shank][trode][window] = math.sqrt(min_error ** 2 + max_error ** 2)

                for trode in range(p['nr_of_electrodes_per_shank']):
                    figure()
                    plot(windows, evoked_window_amps[probe][shank][trode], 'k-')
                    xlabel('Time (min)')
                    ylabel('Peak voltage (uV)')
                    ylim_min = np.floor(np.min(evoked) / 100) * 100
                    ylim_max = np.ceil(np.max(evoked) / 100) * 100
                    ylim(ylim_min, ylim_max)
                    errorbar(windows, evoked_window_amps[probe][shank][trode], yerr = evoked_window_peak_errs[probe][shank][trode])
                    savefig(analyzed_path_for_shank + 'tw_svg_format/' +'/electrode' + str(trode) + '_time_windows.svg', format = 'svg')
                    savefig(analyzed_path_for_shank + 'tw_pdf_format/' +'/electrode' + str(trode) + '_time_windows.pdf', format = 'pdf')
                    lfp_averages[probe][shank][trode]=evoked_window_amps[probe][shank][trode]
                    #evoked_window_peak_errs[probe][shank][trode]
                    close()

                #Save the window LFP analysis in a pickle file
                lfp_averages=np.array(lfp_averages)
                np.save(analyzed_path_for_folder +'/lfp_averages_probe_{:g}_group_{:g}.npy'.format(probe,shank), lfp_averages) # save averages as npy folder, use combining_graphs script for combining the result of several recordings
                np.save(analyzed_path_for_folder +'/evoked_window_peak_errs_probe_{:g}_group_{:g}.npy'.format(probe,shank), evoked_window_peak_errs) # save errors
                save_file = analyzed_path_for_folder + '/probe_{:g}_group_{:g}/probe_{:g}_group_{:g}_window_LFP.pickle'.format(probe,shank,probe,shank)
                pickle.dump({'evoked_window_avgs':evoked_window_avgs, 'evoked_window_err':evoked_window_err}, open(save_file, 'wb'), protocol = -1)
