#this script reads and analyzed single electrode raw data
#Mehmet Ozdas, 18/11/2017

import os 
import numpy as np 
import math

from sklearn.mixture import *
from sklearn.cluster import *
from scipy import signal
from scipy import stats as st
from matplotlib.pyplot import *
from pandas import *
from read_dat_file import *


experiment_path = '/Users/mehmetozdas/Desktop/2017_11_16_FUSs1_EphysM1_E-FUS_NBBB18/FUS_Muscimol_Run1_171116_141234'
#experiment_path = '/home/oce/Desktop/TestExperiments/SlowWaveData/spont_170718_130928'
save_path = experiment_path + '/analyzed'
if not os.path.exists(save_path):
     os.mkdir(save_path)
amplifier_name = 'amp-A-021' # amp-A-001.dat, name of chanel you want to read.
amplifier_path = experiment_path + '/' + amplifier_name + '.dat'
time_path = experiment_path + '/time.dat'
print(amplifier_name)
#NECESSARY COEFFICIENTS

#Filtering Options
low = 300
#high = 300

#Sampling Rates
ds_freq = 2000 #downsampling frequency
sample_rate = 30000

#rms Up/Down classification coefficients
rms_time_width = 0.1 #in s
down_threshold = 90 #uV From minimum
up_threshold = 100 #uV From minimum

DOWN_STATE = -1 #Constant for class
UP_STATE =  1 # Constant for class
NO_STATE = 0 

#evoked LFP coefficients
pre_stim = 50 #ms
post_stim = 150 #ms


print('reading amp file....')
amp_raw_data = read_amplifier_dat_file(amplifier_path)
print('reading time stamp...')
time_file = read_time_dat_file(time_path,sample_rate)
time_s=len(amp_raw_data)/30000 # total recording time
time_m= round(time_s/60)
a=len(amp_raw_data)/time_m
a=round(a)
t1=12.723  #t1=12.213 #240ms
t2=12.727 #t2=12.217
#plot(amp_raw_data[0:60000000], 'k-')
#plot(amp_raw_data[round(t1*a):round(t2*a)], 'k-')
#plot(time_file[round(t1*a):round(t2*a)], amp_raw_data[round(t1*a):round(t2*a)], 'k-')
#time_xs=np.linspace(0.03335649756775538, 240, num=7195) # 240ms
time_xm=np.linspace(5.544593158527964e-07, 38, num=68354880) # 240ms
#plot(time_xs, amp_raw_data[round(t1*a):round(t2*a)], 'k-')
plot(time_xm, amp_raw_data, 'k-')
xlabel('Time (mins)')
ylabel('Peak voltage (uV)')
ylim(-1800,1800) #change this depending on LFP amplitude, this is for vM1
show()
close()
