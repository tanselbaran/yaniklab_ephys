"""
Created on Friday, Oct 6th, 2017

author: Tansel Baran Yasar

Contains the functions for assessing the quality of clustering.
"""

import numpy as np
from matplotlib.pyplot import *
import math
from scipy.spatial.distance import mahalanobis


def cluster_waveform_stdevs(clusters, waveforms, params):
	cluster_inds = calculate_cluster_inds(clusters)
	cluster_waveforms = obtain_unit_waveforms(clusters, waveforms)
	cluster_stdevs = np.zeros(len(cluster_inds))
	for cluster in range(len(cluster_inds)):
		cluster_stdev = np.std(cluster_waveforms[cluster], 0)
		cluster_stdevs[cluster] = np.mean(cluster_stdev)
	return cluster_stdevs

def calculate_distances_from_origin(clusters):
	centers = clusters.cluster_centers_
	centers_sq = np.square(centers)
	centers_sum = np.sum(centers_sq, 1)
	centers_sqrt = np.sqrt(centers_sum)
	return(centers_sqrt)

def calculate_mahalanobis_distances(clusters, projection, params):
	cluster_inds = calculate_cluster_inds(clusters)
	centers = clusters.cluster_centers_
	num_clusters = len(cluster_inds)
	num_channels = len(params['channels'])
	mah_dists = np.zeros((num_clusters, num_clusters))

	for cluster in range(num_clusters):
		cluster_points =projection[cluster_inds[cluster]]
		cluster_points = np.transpose(cluster_points)
		cov_cluster = np.cov(cluster_points)
		center0 = np.reshape(centers[cluster], (projection.shape[1], num_channels))
		for cluster1 in range(num_clusters):
			center1 = np.reshape(centers[cluster1], (projection.shape[1], num_channels))
			a = np.matmul(np.linalg.inv(cov_cluster), (center1-center0))
			dist_sq = np.matmul(np.transpose(center1-center0), a)
			dist = math.sqrt(dist_sq)
			mah_dists[cluster, cluster1] = dist

	return mah_dists

def calculate_unit_distances_from_origin(unit_indices, projection):
    centers = np.mean(projection[unit_indices], 0)
    centers_sq = np.square(centers)
    centers_sum = np.sum(centers_sq, 1)
    centers_sqrt = np.sqrt(centers_sum)
    return(centers_sqrt)

def calculate_mahalanobis_distances_for_units(unit_indices, projection, num_channels):
    centers = np.zeros((projection.shape))
    mah_dists = np.zeros((len(unit_indices), len(unit_indices)))

    for unit in range(len(unit_indices)):
        centers[unit] = np.mean(projection[unit_indices[unit]], 0)
    for unit in range(len(unit_indices)):
        cluster_points = projection[unit_indices[unit]]
        cluster_points = np.transpose(cluster_points)
        cov_cluster = np.cov(cluster_points)
        center0 = np.asarray(centers[unit])
        for unit1 in range(len(unit_indices)):
            center1 = np.asarray(centers[unit1])
            mah_dists[unit, unit1] = mahalanobis(center1, center0, cov_cluster)
    return mah_dists


def ISI(spike_times, sample_rate):
	ISI = {}
	for i in range(len(spike_times)):
		ISI[i] = (np.diff(spike_times[i]) / sample_rate) * 1000
	return ISI

def ISI_violations(ISI, cutoff):
	ISI_violations = np.zeros(len(ISI))
	for i in range(len(ISI)):
		ISI_violation_instances = ISI[i][(np.where(ISI[i] < cutoff))]
		ISI_violations[i] = len(ISI_violation_instances) / len(ISI[i])
	return ISI_violations
