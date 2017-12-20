#this script was used only for tests 18/11/2017, Mozdas
#this part was written by Mehmet Ozdas for Mac (based on Baran Yasar's scripts)
#the only difference for Mac was adding  to dirs list (folder != '.DS_Store')
import numpy as np
import numpy
import pickle
import os
import sys
import ipywidgets
import math
import shutil
from matplotlib.pyplot import *
#from ipywidgets import VBox, HBox
#from IPython.display import display
#saving array to a txt file
#x = y = z = np.arange(0.0,5.0,1.0)
# np.savetxt('test.txt', x, delimiter=',')   # X is an array
#text_file = open("test.txt", "r")
#lines = text_file.readlines()
#input variables
main_path='/mnt/e59fbd77-1f9b-46e9-b00d-7ff44ab2c517/2017_12_12_FUSs1_EphysM1_E-FUS_NBBB25/'  # with / at the end.
tw=2 # time window value
shank_to_plot=1
trode_to_plot=5


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
            tw_pdf_format = analyzed_path_for_shank + 'tw_pdf_format/' # for saving images in pdf format

            if os.path.exists(tw_pdf_format): # if file exist, delete remove old files
                shutil.rmtree(tw_pdf_format)

            if not os.path.exists(tw_pdf_format): # if not, create folder
                os.mkdir(tw_pdf_format)

            tw_svg_format = analyzed_path_for_shank + 'tw_svg_format/'
            if os.path.exists(tw_svg_format):   # if file exist, delete remove old files
                shutil.rmtree(tw_svg_format)

            if not os.path.exists(tw_svg_format): # create  a new fiel and store images here
                os.mkdir(tw_svg_format)

            average_evoked_LFP_at_time_pdf_format = analyzed_path_for_shank + 'avg_eLFP_tw_pdf_format/'

            if os.path.exists(average_evoked_LFP_at_time_pdf_format): # if file exist, delete remove old files
                shutil.rmtree(average_evoked_LFP_at_time_pdf_format)

            if not os.path.exists(average_evoked_LFP_at_time_pdf_format):
                os.mkdir(average_evoked_LFP_at_time_pdf_format)

            average_evoked_LFP_at_time_svg_format = analyzed_path_for_shank + 'avg_eLFP_tw_svg_format/'

            if os.path.exists(average_evoked_LFP_at_time_svg_format): # if file exist, delete remove old files
                shutil.rmtree(average_evoked_LFP_at_time_svg_format)

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
            lfp_averages=numpy.zeros((p['probes'],p['shanks'],p['nr_of_electrodes_per_shank'],num_window))

            for window in range(num_window):
                 print("Time: {:g}".format(window))
                 #Finding all the evoked data for which the time stamp falls in the window of interest
                 evoked_window = evoked[np.all([stim_timestamps > window * len_time_window, stim_timestamps < (window + 1) * len_time_window], axis = 0)]
                 evoked_window_avgs[window] = np.mean(evoked_window, 0) #  mean of evoked window
                 evoked_window_std = np.std(evoked_window, 0) #Standard deviation of the data in the time window
                 evoked_window_err[window] = evoked_window_std / math.sqrt(len(evoked_window)) # standart error of evoked window
                 #Plotting and saving the figure for the average evoked LFP in this time window
                 if shank_to_plot == shank:
                    trode = trode_to_plot
                    figure()
                    plot(evoked_LFP_timerange, evoked_window_avgs[window][trode],'k-')
                    xlabel('Time (ms)')# analyzed_path_for_folder
                    ylabel('Peak voltage (uV)')
                    ylim_min = np.floor(np.min(evoked) / 100) * 100
                    ylim_max = np.ceil(np.max(evoked) / 100) * 100
                    ylim(ylim_min, ylim_max)
                    #ylim(-2500,300) #change this depending on LFP amplitude, this is for vM
                    fill_between(evoked_LFP_timerange, evoked_window_avgs[window][trode]-evoked_window_err[window][trode], evoked_window_avgs[window][trode]+evoked_window_err[window][trode])
                    print('plotting windows figures and saving')
                    savefig(average_evoked_LFP_at_time_pdf_format +'average_evoked_LFP_at_time_{:g}_for_group_{:g}_electrode_{:g}'.format(window*tw, shank, trode)+'.pdf', format = 'pdf')
                    savefig(average_evoked_LFP_at_time_svg_format +'average_evoked_LFP_at_time_{:g}_for_group_{:g}_electrode_{:g}'.format(window*tw, shank, trode)+'.svg', format = 'svg')
                    #savefig(analyzed_path_for_shank + 'average_evoked_LFP_at_time_window_{:g}_for_shank_{:g}_electrode_{:g}'.format(window, shank, trode)+'.pdf', format = 'pdf')
                    #savefig(analyzed_path_for_shank + 'average_evoked_LFP_at_time_window_{:g}_for_shank_{:g}_electrode_{:g}'.format(window, shank, trode)+'.svg', format = 'svg')
                    #savefig(analyzed_path_for_shank + 'average_evoked_LFP_at_time_window_{:g}_for_shank_{:g}_electrode_{:g}'.format(window, shank, trode), format = 'svg')
                    #savefig(analyzed_path_for_shank + 'average_evoked_LFP_at_time_window_{:g}_for_shank_{:g}_electrode_{:g}'.format(window, shank, trode), format = 'pdf')
                    close()
                 for trode in range(p['nr_of_electrodes_per_shank']):
                    evoked_window_amps[probe][shank][trode][window] = np.min(evoked_window_avgs[window][trode])
                    min_error = evoked_window_err[window][probe][np.where(evoked_window_avgs[window][trode] == np.min(evoked_window_avgs[window][trode]))]
                    if len(min_error) == 1:
                        evoked_window_peak_errs[probe][shank][trode][window] = min_error

            for trode in range(p['nr_of_electrodes_per_shank']):
                figure()
                plot(windows, evoked_window_amps[probe][shank][trode], 'k-')
                xlabel('Time (min)')
                ylabel('Peak voltage (uV)')
                ylim_min = np.floor(np.min(evoked) / 100) * 100
                ylim_max = np.ceil(np.max(evoked) / 100) * 100
                ylim(ylim_min, ylim_max)
                #ylim(-2500,300) #change this depending on LFP amplitude, this is for vM1
                errorbar(windows, evoked_window_amps[probe][shank][trode], yerr = evoked_window_peak_errs[probe][shank][trode])
                savefig(analyzed_path_for_shank + 'tw_svg_format/' +'/electrode' + str(trode) + '_time_windows.svg', format = 'svg')
                savefig(analyzed_path_for_shank + 'tw_pdf_format/' +'/electrode' + str(trode) + '_time_windows.pdf', format = 'pdf')
                lfp_averages[probe][shank][trode]=evoked_window_amps[probe][shank][trode]
                #evoked_window_peak_errs[probe][shank][trode]
                close()
            #Save the window LFP analysis in a pickle file
            print("windows")
            print(windows)
            lfp_averages=numpy.array(lfp_averages)
            np.save(analyzed_path_for_folder +'/lfp_averages_probe_{:g}_group_{:g}.npy'.format(probe,shank), lfp_averages) # save averages as npy folder, use combining_graphs script for combining the result of several recordings
            np.save(analyzed_path_for_folder +'/evoked_window_peak_errs_probe_{:g}_group_{:g}.npy'.format(probe,shank), evoked_window_peak_errs) # save errors
            save_file = analyzed_path_for_folder + '/probe_{:g}_group_{:g}/probe_{:g}_group_{:g}_window_LFP.pickle'.format(probe,shank,probe,shank)
            pickle.dump({'evoked_window_avgs':evoked_window_avgs, 'evoked_window_err':evoked_window_err}, open(save_file, 'wb'), protocol = -1)
            evoked_window_peak_errs[probe][shank][trode][window] = min_error
