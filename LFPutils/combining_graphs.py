#this script is used to combine graphs from different recordings.
#Mehmet Ozdas 18/11/2017
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
#shank_to_plot=1
#trode_to_plot=1
dirs=os.listdir(main_path)
all_av = []
all_err = []
folders = sorted((folder for folder in dirs if ((folder != 'log.txt') and (folder != 'notes.docx') and (folder != 'other') and (folder != '.DS_Store') and (folder != 'analyzed') and (folder != 'analysis_files'))))
p = pickle.load(open(main_path + '/' + folders[0] + '/paramsDict.p', 'rb'))

analyzed_path = main_path + 'analyzed/' + 'all_tw/'
if not os.path.exists(analyzed_path):
	os.mkdir(analyzed_path)

tw_pdf = analyzed_path + 'pdf/'
if not os.path.exists(tw_pdf):
	os.mkdir(tw_pdf)

tw_svg = analyzed_path + 'svg/'
if not os.path.exists(tw_svg):
	os.mkdir(tw_svg)

for probe in range(p['probes']):
	for shank in range(p['shanks']):
		for trode in range(p['nr_of_electrodes_per_shank']):
			for folder in folders:
				print(probe, shank, trode, folder)
				analyzed_path_for_folder = main_path + 'analyzed/' + folder
				path_av=analyzed_path_for_folder+"/lfp_averages_probe_{:g}_group_{:g}.npy".format(probe,shank)
				path_er=analyzed_path_for_folder+"/evoked_window_peak_errs_probe_{:g}_group_{:g}.npy".format(probe,shank)
				av=np.load(path_av)
				er=np.load(path_er)
				all_av=np.append(all_av,av[probe,shank,trode,:])
				all_err=np.append(all_err,er[probe,shank,trode,:])
			windows=len(all_av)
			a=np.linspace(0, windows*2, num=windows)
			figure()
			plot(a, all_av, 'k-')
			xlabel('Time (min)')
			ylabel('Peak voltage (uV)')
			ylim(-2500,300) #change this depending on LFP amplitude, this is for vM1
			errorbar(a, all_av, yerr = all_err)

			savefig(tw_svg + 'Run2_time_windows_probe_{:g}_group_{:g}_trode_{:g}.svg'.format(probe,shank,trode), format = 'svg')
			savefig(tw_pdf + 'Run2_time_windows_probe_{:g}_group_{:g}_trode_{:g}.pdf'.format(probe,shank,trode), format = 'pdf')
			close()
			all_av = []
			all_err = []
