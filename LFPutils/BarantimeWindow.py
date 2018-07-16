p = pickle.load(open(mp.value + '/' + fn.value + '/paramsDict.p', 'rb')) #Loading parameter dictionary
len_time_window = tw.value * 60 * p['sample_rate'] #Converting the time window length from minutes to number of samples
analyzed_path_for_folder = mp.value + '/analyzed/' + fn.value

for probe in range(p['probes']):
    for shank in range(p['shanks']):
        analyzed_path_for_shank = analyzed_path_for_folder + '/probe_{:g}_group_{:g}/'.format(probe,shank)

        #Loading the evoked LFP data from the evoked LFP pickle saved by the evoked_LFP_analysis.py script
        data_location = mp.value + '/' + fn.value + ('/probe_{:g}_group_{:g}'.format(probe,shank)) + ('/probe_{:g}_group_{:g}_evoked.pickle'.format(probe,shank))
        evoked_data = pickle.load(open(data_location, 'rb'))
        evoked = evoked_data['evoked']
        stim_timestamps = evoked_data['stim_timestamps']

        num_window = int(np.max(stim_timestamps) / len_time_window) #Calculating number of time windows in data
        windows = np.arange(0,num_window,1)

        evoked_window_avgs = np.zeros((num_window, len(evoked[0]), len(evoked[0][0]))) #Averages of the evoked LFPs over time window
        evoked_window_err = np.zeros((num_window, len(evoked[0]), len(evoked[0][0]))) #Standard errors of the evoked LFPs over time window
        evoked_window_amps = np.zeros((p['probes'], p['shanks'], p['nr_of_electrodes_per_shank'], num_window)) #Amplitude of the evoked LFPs over time window
        evoked_window_peak_errs = np.zeros((p['probes'], p['shanks'], p['nr_of_electrodes_per_shank'], num_window)) #Error of the amplitude of the evoked LFPs over time window

        for window in range(num_window):
            print("Time: {:g}".format(window))
            evoked_window = evoked[np.all([stim_timestamps > window * len_time_window, stim_timestamps < (window + 1) * len_time_window], axis = 0)] #Finding all the evoked data for which the time stamp falls in the window of interest
            evoked_window_avgs[window] = np.mean(evoked_window, 0)
            evoked_window_std = np.std(evoked_window, 0) #Standard deviation of the data in the time window
            evoked_window_err[window] = evoked_window_std / math.sqrt(len(evoked_window)) #Standard error of the evoked LFP data in the time window

            for trode in range(p['nr_of_electrodes_per_shank']):
                evoked_window_amps[probe][shank][trode][window] = np.max(evoked_window_avgs[window][trode]) - np.min(evoked_window_avgs[window][trode]) #Amplitude of the average evoked LFP
                min_error = evoked_window_err[window][probe][np.where(evoked_window_avgs[window][trode] == np.min(evoked_window_avgs[window][trode]))] #Standard error at the min value
                max_error = evoked_window_err[window][probe][np.where(evoked_window_avgs[window][trode] == np.max(evoked_window_avgs[window][trode]))] #Standard error at the max value
                if len(min_error) == 1:
                    evoked_window_peak_errs[probe][shank][trode][window] = math.sqrt(min_error ** 2 + max_error ** 2)

        for trode in range(p['nr_of_electrodes_per_shank']):
            figure()
            plot(windows, evoked_window_amps[probe][shank][trode], 'k-')
            xlabel('Time (min)')
            ylabel('Peak voltage (uV)')
            errorbar(windows, evoked_window_amps[probe][shank][trode], yerr = evoked_window_peak_errs[probe][shank][trode])
            savefig(analyzed_path_for_shank + '/electrode' + str(trode) + '_time_windows.svg', format = 'svg')
            close()

        #Save the window LFP analysis in a pickle file
        save_file = analyzed_path_for_folder + '/probe_{:g}_group_{:g}/probe_{:g}_group_{:g}_window_LFP.pickle'.format(probe,shank,probe,shank)
        pickle.dump({'evoked_window_avgs':evoked_window_avgs, 'evoked_window_err':evoked_window_err}, open(save_file, 'wb'), protocol = -1)
