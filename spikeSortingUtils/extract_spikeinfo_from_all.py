"""
Created on Tuesday, Aug 8th 2017

author: Tansel Baran Yasar

Containing the script for running through all recording sessions in the experiment for extracting the spike information clu files.

Usage: Recommended usage through the Jupyter notebook for spike sorting. For standalone usage,
run this script from bash as following:
    PATHEXP="/dir/to/the/folder/recording/subfolders/for/the/recording/sessions/"
    echo $PATHEXP|python extract_spikeinfo_from_all.py
"""

import pickle
import os
import sys
from spike_postprocessing_utils import *

mainPath = sys.stdin.read().splitlines()[0] #Reads the mainPath from bash input.
"""dirs = os.listdir(mainPath)

for folder in (folder for folder in dirs if ((folder != 'log.txt') and (folder != 'notes.docx') and (folder != 'analyzed') and (folder != 'other'))):
    #Iterating over the folders for individual recording sessions, while skipping other files and folders.
    #All files/folders in the experiment folder that are not log, notes or analyzed should be grouped in a folder named 'other'
    print(mainPath + folder) #printing the recording session that is being analyzed
    p = pickle.load(open(mainPath + folder + '/paramsDict.p', 'rb')) #Loading the params_dict dictionary

    for probe in range(p['probes']):
        for group in range(p['nr_of_groups']):
            retain_cluster_info(probe,group,p)"""

folder = 'analysis_files'
p =  pickle.load(open(mainPath + folder + '/paramsDict.p', 'rb'))
for probe in range(p['probes']):
    for group in range(p['nr_of_groups']):
        retain_cluster_info(probe,group,p)
