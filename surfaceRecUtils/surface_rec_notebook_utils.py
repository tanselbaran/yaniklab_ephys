import numpy as np
from matplotlib.pyplot import *
from mpl_toolkits.mplot3d import Axes3D
from utils.filtering import *
from utils.load_intan_rhd_format import *
from utils.reading_utils import *
from tqdm import tqdm
from LFPutils.read_evoked_lfp import *
import pickle as p
from ipywidgets import interact, IntText, fixed, FloatSlider
from IPython.display import display


###Utilities for pre-processing data (reading , filtering , thresholding)

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
        waveforms_session = np.zeros((0, len(channels), 60))
        peak_times_session = np.zeros(0)

        for trode in range(len(params['channels'])):
            if params['channels'][trode] < 10:
                filepath = params['mainfolder'] + 'amp-A-00' + str(params['channels'][trode]) + '.dat'
            else:
                filepath = params['mainfolder'] + 'amp-A-0' + str(params['channels'][trode])  + '.dat'
            data_electrode[trode] = read_amplifier_dat_file(filepath)

        if global_params['spike_sorting'] == True:
            bandfilt = global_params['bandfilt']
            filtered_data_electrode = bandfilt(data_electrode)
            (waveforms_trode, peak_times_trode) = extract_waveforms(filtered_data_electrode, params)
            waveforms_session = np.append(waveforms_session, waveforms_trode, 0)
            peak_times_session = np.append(peak_times_session, peak_times_trode + current_end_time)

        data = np.append(data, data_electrode, 1)
        stim = np.append(stim, params['stim'])
        waveforms = np.append(waveforms, waveforms_session, 0)
        peak_times = np.append(peak_times, peak_times_session,0)
        current_end_time = current_end_time + params['time'][-1]
        end_inds[rec] = np.sum((end_times*global_params['sample_rate'])[0:rec+1]) + rec
    end_inds = np.insert(end_inds,0,0)

    if global_params['spike_sorting'] == True:
        location_output = {'waveforms': waveforms, 'data':data, 'peak_times':peak_times, 'stim':stim, 'time':time, 'end_inds':end_inds}
    else:
        location_output = {'data':data, 'stim':stim, 'time':time, 'end_inds':end_inds}

    return location_output

def extract_waveforms(data, params):
	"""
	This function extracts waveforms from multiple channel data based on the
	given threshold coefficient. A relative threshold is calculated by
	multiplying the rms of the recording with the given threshold coefficient.
	For each time step the function scans through all the electrodes to find an
	event of threshold crossing. If so, the waveforms in all channels surrounding
	that time step are recorded.

	Inputs:
		data: Numpy array containing the bandpass filtered data in the form of
			(N_electrodes x N_time steps)
		params: Dictionary containing the recording parameters. The following
			entries must be present:

			sample_rate: Sampling rate in Hz
			time: Time array of the recording (numpy array)
			pre: Extent of the spike time window prior to peak (in ms)
			post: Extent of the spike time window post the peak (in ms)
			flat_map_array: Flattened numpy array containing the spatial
				information of the electrodes (contains only one element
				for single channel recordings)
			threshold_coeff: Coefficient used for calculating the threshold
				value per channel

	Outputs:
		waveforms: Numpy array containing the extracted waveforms from all
			channels (N_events x N_electrodes x N_timesteps_in_spike_time_range)
		peak_times: numpy array containing the times of the events (in s)
			(1xN_events)
	"""

	noise = np.sqrt(np.mean(np.square(data), 1))
	threshold = (-1) * noise * params['threshold_coeff']

	waveforms = []
	peak_times = []
	found = False
	for i in tqdm(range(len(params['time'])-40)):
		for trode in range(len(params['channels'])):
			if (data[trode,i] < threshold[trode]) and (abs(data[trode,i]) > abs(data[trode,i-1])) and (abs(data[trode,i]) > abs(data[trode,i+1])):
				found = True
				break
		if found and (i > len(params['spike_timerange'])):
			waveform = np.zeros((len(params['channels']), len(params['spike_timerange'])))
			for trode in range(len(params['channels'])):
				waveform[trode,:] = data[trode, (i-int(params['pre']*params['sample_rate']/1000)):(i+int(params['post']*params['sample_rate']/1000))]
			waveforms.append(waveform)
			peak_times.append(params['time'][i])
			found = False

	waveforms = np.asarray(waveforms)
	peak_times = np.asarray(peak_times)
	return waveforms, peak_times


def surface_evoked_LFP(location_output, begin, end, global_params, mode):
    if mode == 'evoked':
        stim_timestamps = extract_stim_timestamps_der(location_output['stim'])
    if mode == 'spont':
        stim_timestamps = np.arange(begin, end, global_params['sample_rate'])
    lowfilt = lowpassFilter(rate = global_params['sample_rate'], high = 300, order = 4)
    filtered_data = lowfilt(location_output['data'])
    evoked = read_evoked_lfp_from_stim_timestamps(filtered_data, begin, end, stim_timestamps, global_params)
    return evoked


### Utilities for processing the units

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

def get_unit_spike_times_and_trains(unit_indices, time, peak_times, global_params):
    spike_times = {}
    spike_trains = np.zeros((len(unit_indices), len(time)))

    for unit in range(len(unit_indices)):
        spike_times_ind = peak_times[unit_indices[unit]]
        spike_times_ind = np.asarray(spike_times_ind * global_params['sample_rate'])
        spike_times_ind = spike_times_ind.astype(int)
        spike_times[unit] = np.sort(spike_times_ind)
        spike_trains[unit][spike_times_ind] = 1

    return spike_times, spike_trains

### Utilites for plotting

def plot_waveforms(index, waveforms, plot_params, params):
	"""
	This function serves as the interactive function for the widget for displaying waveforms across multiple channels.

	Inputs:
		index: Index of the waveform to be displayed [int]
		waveforms: Numpy array containing the waveforms; in the form of (N_events x N_electrodes x N_spike_time_range_steps)
		mapping: Mapping attribute in the h5 data
		plot_params: Dictionary containing parameters related to plotting. Must contain following entries:
			nrow: Number of rows in the subplot grid
			ncol: Number of columns in the subplot grid
			ylim: Limits of the y axis for all electrodes, in the form of [ymin, ymax]
		params: Dictionary containing recording parameters
			flat_map_array: Flattened numpy array containing the spatial mapping information of the electrodes
			spike_timerange: Array containing the time range of the spike time window
	"""

	fig, axs = subplots(plot_params['nrow'], plot_params['ncol'])
	channel = 0
	for i, ax in enumerate(fig.axes):
		ax.plot(global_params['spike_timerange'], waveforms[index, channel])
		ax.set_ylim(plot_params['ylim'])
		ax.set_xlabel('Time (ms)')
		ax.set_ylabel('Voltage (uV)')
		channel = channel+1
	show()

def plot_mean_cluster_waveforms(cluster, clusters, waveforms, plot_params, global_params, mode):
	"""
	This function serves as the interactive function for the widget for displaying waveforms across multiple channels.

	Inputs:
		cluster: Index of the cluster for which the waveforms to be displayed [int]
		clusters: Result of the k-means clustering on the projection of the waveforms on the principal component axes
		waveforms: Numpy array containing the waveforms; in the form of (N_events x N_electrodes x N_spike_time_range_steps)
		mapping: Mapping attribute in the h5 data
		plot_params: Dictionary containing parameters related to plotting. Must contain following entries:
			nrow: Number of rows in the subplot grid
			ncol: Number of columns in the subplot grid
			ylim: Limits of the y axis for all electrodes, in the form of [ymin, ymax]
		params: Dictionary containing recording parameters
			flat_map_array: Flattened numpy array containing the spatial mapping information of the electrodes
			spike_timerange: Array containing the time range of the spike time window
		mode: Plot the mean waveform with or without the individual waveforms ('ind_on' for displaying the individual waveforms, 'ind_off' for not displaying them)
	"""

	#Selecting the spike waveforms that belong to the selected cluster and calculating the mean waveform at each electrode
	spikes_in_cluster = waveforms[np.where(clusters.labels_ == cluster)]
	mean_spikes_in_cluster = np.mean(spikes_in_cluster, 0)

	fig, axs = subplots(plot_params['nrow'], plot_params['ncol'])
	channel = 0
	for i, ax in enumerate(fig.axes):
		ax.plot(global_params['spike_timerange'], mean_spikes_in_cluster[channel])
		if mode == 'ind_on':
			for spike in range(len(spikes_in_cluster)):
				ax.plot(global_params['spike_timerange'], spikes_in_cluster[spike,i], 'b', alpha = 0.1)
		ax.set_ylim(plot_params['ylim'])
		ax.set_xlabel('Time (ms)')
		ax.set_ylabel('Voltage (uV)')
		channel = channel + 1
	show()

def plot_3d_of_clusters(clusters, projection, global_params):
	"""
	This function makes a 3d scatter plot of the projections of the spike waveforms  onto the 3 principal axes that count for the highest fraction of variance in the original waveforms array. The scatter points are colored with respect to the clusters that each spike waveform belongs to.

	Inputs:
		clusters: KMeans object that contains information about the results of the K-means clustering of the waveforms projected on the principal component axes
		projection: 2d numpy array (# of spike_events x # of PCA axes) that contains the projections of the spike waveforms on the PCA axes
	"""

	fig = figure()
	ax = fig.add_subplot(111, projection = '3d')
	for cluster in range(clusters.n_clusters):
		cluster_indices = np.where(clusters.labels_ == cluster)
		ax.scatter(projection[:,0][cluster_indices], projection[:,1][cluster_indices], projection[:,2][cluster_indices], global_params['colors'][cluster])
	show()

### IPython widget utilities for interactivity

def display_widget(waveforms, plot_params, global_params, mode, *args):
	"""
	This function creates and displays the widget for selecting the waveform or cluster index to be displayed and the widget that displays
	the waveforms or mean waveforms for the clusters across multiple channels for this index.

	Inputs:
		waveforms: Numpy array containing the waveforms; in the form of (N_events x N_electrodes x N_spike_time_range_steps )
		plot_params: see above
		mapping: Mapping attribute in the h5 data
		params: see above
		mode: 'waveforms' for displaying individual waveforms by index, 'clusters' for displaying the mean waveform of a cluster
	"""
	if mode[0] == 'waveforms':
		#Widget for selecting waveform or cluster index
		selectionWidget = IntText(min=0, max=len(waveforms), step = 1, value = 0,
			description = "Waveforms to be displayed", continuous_update = True)

		#Widget for plotting selected waveforms or mean waveforms
		widget = interact(plot_waveforms, index = selectionWidget,
			waveforms = fixed(waveforms), plot_params = fixed(plot_params), global_params = fixed(global_params))
	elif mode[0] == 'clusters':
		#Widget for selecting waveform or cluster index
		selectionWidget = IntText(min=0, max=len(waveforms), step = 1, value = 0,
			description = "Cluster for which the waveforms to be displayed", continuous_update = True)

		#Widget for plotting selected waveforms or mean waveforms
		widget = interact(plot_mean_cluster_waveforms, cluster = selectionWidget,
			clusters = fixed(args[0]), waveforms = fixed(waveforms),
			plot_params = fixed(plot_params), global_params = fixed(global_params), mode = mode[1])
	else:
		raise ValueError('Please select a valid mode for display ("waveforms" or "clusters")')

	display(selectionWidget)
	display(widget)

### Utilities for long-term storage and retrieval of the analysis results

def save_clusters_to_pickle(clusters, projection, filepath):
	p.dump({'clusters': clusters, 'projection': projection}, open(filepath, 'wb'))

def save_reclusters_to_pickle(clusters, waveforms, projection, peak_times, filepath):
	p.dump({'clusters': clusters, 'waveforms': waveforms, 'peak_times': peak_times, 'projection': projection}, open(filepath, 'wb'))

def read_clusters_from_pickle(filepath):
	cluster_dict = p.load(open(filepath, 'rb'))
	clusters = cluster_dict['clusters']
	projection = cluster_dict['projection']
	return clusters, projection

def read_reclusters_from_pickle(filepath):
	cluster_dict = p.load(open(filepath, 'rb'))
	clusters = cluster_dict['clusters']
	waveforms = cluster_dict['waveforms']
	peak_times = cluster_dict['peak_times']
	projection = cluster_dict['projection']
	return clusters, waveforms, peak_times, projection

def save_waveforms_to_pickle(waveforms, peak_times, filepath):
	p.dump({'waveforms': waveforms, 'peak_times': peak_times}, open(filepath, 'wb'))

def read_waveforms_from_pickle(filepath):
	waveforms_dict = p.load(open(filepath, 'rb'))
	waveforms = waveforms_dict['waveforms']
	peak_times = waveforms_dict['peak_times']
	return waveforms, peak_times
