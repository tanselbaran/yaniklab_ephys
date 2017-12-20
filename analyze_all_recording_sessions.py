"""
Added to GitHub on Tuesday, Aug 1st 2017

author: Tansel Baran Yasar

Containing the script for running through all recording sessions in the experiment for spike sorting or LFP analysis.

Usage: Recommended usage through the Jupyter notebooks for spike sorting or LFP analysis. For standalone usage,
run this script from bash as following:
    PATHEXP="/dir/to/the/folder/recording/subfolders/for/the/recording/sessions/"
    echo $PATHEXP|python analyze_all_recording_sessions.py
"""

from main import main
import pickle
import os
import sys

mainPath = sys.stdin.read().splitlines()[0] #Reads the mainPath from bash input.
dirs = os.listdir(mainPath)

#Counting the number of recording sessions in the experiment
num_sessions = 0
for folder in (folder for folder in dirs if ((folder != 'log.txt') and (folder != 'notes.docx') and (folder != 'analysis_files') and (folder != 'analyzed') and (folder != 'other') and (folder != '.DS_Store'))):
    num_sessions = num_sessions + 1

current_session = 1 #Index for the current recording session that is being analyzed

for folder in sorted((folder for folder in dirs if ((folder != 'log.txt') and (folder != 'notes.docx') and (folder != 'analysis_files') and (folder != 'analyzed') and (folder != 'other') and (folder != '.DS_Store')))):
    #Iterating over the folders for individual recording sessions, while skipping other files and folders.
    #All files/folders in the experiment folder that are not log, notes or analyzed should be grouped in a folder named 'other'

    p = pickle.load(open(mainPath + folder + '/paramsDict.p', 'rb')) #Loading the params_dict dictionary

    #Determining the order of the session among all sessions
    if num_sessions == 1:
        p['order'] = 3
    elif current_session == 1:
        p['order'] = 0
    elif current_session == num_sessions:
        p['order'] = 2
    else:
        p['order'] = 1
    print("Currently analyzing:" + mainPath + folder) #printing the recording session that is being analyzed

    main(p) #Running the main function on the recording session.
    current_session = current_session + 1
