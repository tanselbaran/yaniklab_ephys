from matplotlib.mlab import PCA
from sklearn.cluster import KMeans
from surfaceRecUtils.surface_rec_notebook_utils import *

def PCA_on_waveforms(waveforms, minfrac, params):
	"""
	This function performs principal component analysis on the spike waveforms extracted and returns the
	projection of the waveforms on these principal component axes.

	Inputs:
		waveforms: Numpy array containing the waveforms; in the form of
			(N_events x N_electrodes x N_spike_time_range_steps)
		minfrac: Principal component axes that counts for the variance greater than this minfrac
			value will be taken into account.
		params: Dictionary containing the recording and analysis parameters. Following entries must be present:
			spike_timerange: List containing the time range of spike waveform as an array

	Outputs:
		projection: Waveforms projected on the principal component axes
	"""
	"""peak_of_spike_time_range = (len(params['spike_timerange']) / 2) + 1
	peaks = waveforms[:,:,peak_of_spike_time_range]

	true_electrode_inds = np.where(peaks[0] != 0) #Eliminating the broken or absent electrodes on the grid (for which the voltage equals 0 all the time) in order to avoid their contamination on the PCA.
	waveforms_true = waveforms[:,true_electrode_inds] #Waveforms from absent electrodes eliminated
	n_dimensions = len(true_electrode_inds[0]) * len(params['spike_timerange']) #Number of dimensions before dimensionality reduction
	waveforms_true = waveforms_true.reshape(len(peaks),n_dimensions) #Reshaping the array with respect to initial number of dimensions
	results = PCA(waveforms_true)"""

	n_dimensions = len(waveforms[0]) * len(params['spike_timerange'])
	waveforms = waveforms.reshape(len(waveforms), n_dimensions)
	results = PCA(waveforms)
	#projection = results.project(waveforms_true, minfrac)
	projection = results.project(waveforms, minfrac)
	return projection

def kmeans_clusters(num_clusters, projection):
	"""
	This function performs k-means clustering on the projection of the spike waveforms on the principal
	component axes

	Inputs:
		num_clusters: Number of cluster seeds for the k-means clustering
		projection: Waveforms projected on the principal component axes

	Outputs:
		clusters: KMeans object containing information about the results of K-means clustering
	"""

	clusters = KMeans(n_clusters=num_clusters).fit(projection)

	return clusters

def PCA_and_cluster(waveforms, params, minfrac, num_clusters):
	projection = PCA_on_waveforms(waveforms, 0.01, params)
	clusters = kmeans_clusters(num_clusters, projection)
	#plot_3d_of_clusters(clusters, projection, params)

	return clusters, projection

def recluster(waveforms, params, peak_times, minfrac, num_clusters, old_clusters, good_cluster_indices):

	good_waveform_inds = []
	for good_cluster in good_cluster_indices:
		good_waveform_inds.extend(np.where(old_clusters.labels_ == good_cluster)[0])
	good_waveforms = waveforms[good_waveform_inds,:,:]
	(good_clusters, good_projection) = PCA_and_cluster(good_waveforms, params, minfrac, num_clusters)
	good_peaktimes = peak_times[good_waveform_inds]
	return good_clusters, good_waveforms, good_peaktimes, good_projection
