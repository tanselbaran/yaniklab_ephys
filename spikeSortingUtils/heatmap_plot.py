"""
Added to GitHub on Tuesday, Aug 1st 2017

authors: Clemens Dlaska and Tansel Baran Yasar

Contains the source code for generating the 2D histogram of waveforms in a cluster, as part of the custom GUI. 

Usage: Called from the gui.py for adding the heatmap plot to the custom GUI.
"""

import numpy as np
from pylab import *
import pickle
from scipy import interpolate
from scipy.stats import norm


def generate_heatmap(c,e,main_dict):
    """
    This function generates a 2D histogram of the spike waveforms of a cluster, in the form of a heatmap. 
    
    Inputs:
        h: Height index of the tetrode on the shank (0 corresponding to bottom-most)
        s: Shank index (0 corresponding to left-most, on the electrode side)
        c: Cluster index
        e: Index for the electrode in the tetrode (0 corresponding to bottom-most, increasing clock-wise)
        main_dict: Dictionary containing the waveforms, spike time info and the parameters dictionary
        
    Output: The 2D heatmap as a plot.
    """
    
    nr_of_spikes = main_dict['P']['c{:g}'.format(c)][1].shape[0]
    nr_of_timepoints = main_dict['P']['c{:g}'.format(c)][1].shape[2]
    waveforms = np.array([main_dict['P']['c{:g}'.format(c)][1][i][e][:] for i in range(nr_of_spikes)])
    max_val = max([max(waveforms[i]) for i in range(nr_of_spikes)])
    min_val = min([min(waveforms[i]) for i in range(nr_of_spikes)])
    range_val = max_val - min_val
    steps = range_val/200
    x = range(nr_of_timepoints)
    y_intervals= frange(min_val,max_val,steps)
    y = frange(min_val+steps/2,max_val-steps/2,steps)

    
    intensity = np.zeros((len(x),len(y)))
    for i in range(len(x)):
        for j in range(len(y)):
            for k in range(nr_of_spikes):
                if waveforms[k,i] > y_intervals[j] and waveforms[k,i] < y_intervals[j+1]:
                    intensity[i,j] = intensity[i,j] + 1
    
    x, y = np.meshgrid(x,y)
    pcolormesh(x,y,intensity.transpose())
    colorbar()
    show()
    
def g(x,y_res,min_val,max_val):
    val = floor((y_res-2)*(x-min_val)/(max_val-min_val)+2.5)
    return val
    
def g_inv(y,y_res,min_val,max_val):
    val = floor(((y-2.5)*(max_val-min_val))/(y_res-2) + min_val)
    return val
    

def generate_heatmap_interpolated(c,e,main_dict):
    """
    This function generates a 2D histogram of the spike waveforms of a cluster, in the form of a heatmap. In contrast to the previous function, this function generates the map with each pixel blurred by a Gaussian blur. 
    
    Inputs:
        c: Cluster index
        e: Index for the electrode in the tetrode (0 corresponding to bottom-most, increasing clock-wise)
        main_dict: Dictionary containing the waveforms, spike time info and the parameters dictionary
        
    Output: The 2D heatmap as a plot.
    """
    
    p = main_dict['p']
    nr_of_spikes = main_dict['P']['c{:g}'.format(c)][1].shape[0]
    nr_of_timepoints = main_dict['P']['c{:g}'.format(c)][1].shape[2]
    waveforms = np.array([main_dict['P']['c{:g}'.format(c)][1][i][e][:] for i in range(nr_of_spikes)])
    
    # Define resolution:
    t_res = 200
    y_res = 201
    
    # Average standard deviation
    avg_std = np.mean(np.std(waveforms))
    
    # Standard deviation for Gaussian
    std_gauss = avg_std/5
    
    # Data interpolation
    interpolated_waveforms = np.zeros((nr_of_spikes,t_res))
    x = np.arange(nr_of_timepoints)
    x_new = np.linspace(0,nr_of_timepoints-1,t_res)
    for i in range(nr_of_spikes):
        y = waveforms[i]
        f = interpolate.interp1d(x, y, kind='cubic')
        interpolated_waveforms[i,:] = f(x_new)
        
    # Define function for bin of a data point
    min_val = min([min(waveforms[i]) for i in range(nr_of_spikes)]) - std_gauss*5
    max_val = max([max(waveforms[i]) for i in range(nr_of_spikes)]) + std_gauss*5
    
    # Size of Gaussian blur
    gauss_width = round(std_gauss/(max_val - min_val)*y_res*3)
    
    gauss = norm.pdf(np.arange(-gauss_width,gauss_width+1),0,gauss_width/3)
    gauss = gauss/sum(gauss)
    
    # Fill bins
    bins = np.zeros((t_res,y_res))
    for i in range(t_res):
        for j in range(nr_of_spikes):
            bin = 1 + y_res-g(interpolated_waveforms[j,i],y_res,min_val,max_val)
            #for k in np.arange(-gauss_width,gauss_width):
            bins[i,int(bin)] = bins[i,int(bin)] + 1
    
    # Convolve signal
    psf = np.pad(gauss, int((y_res-2*int(gauss_width)-1)/2), 'constant')
    gauss_bins= np.empty([t_res,y_res])
    
    #print(psf)
    #print(gauss_bins.shape)
    
    for i in range(t_res):
        gauss_bins[i,:] = np.convolve(bins[i,:],psf,'same')
        
    gauss_bins = gauss_bins/np.amax(gauss_bins)
 
    # Generate heatmap plot
    x = linspace(0,nr_of_timepoints-1, t_res)/(p['sample_rate']/1000)
    y = [g_inv(i,y_res,min_val,max_val) for i in range(y_res)] 
    x, y = np.meshgrid(x,y)
    plt=figure()
    pcolormesh(x,y,np.fliplr(gauss_bins).transpose())
    xlabel(r'$t\, [\mathrm{ms}]$')
    ylabel(r'$V\, [\mu\mathrm{V}]$')
    colorbar()
    show()
               
    
