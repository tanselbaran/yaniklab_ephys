import sys
from load_intan_rhd_format import *
from read_probe import *
from time import time
from data_processing_utils import *
from pylab import *
from heatmap_plot import *
from read_evoked_lfp import read_evoked_lfp
import pickle

def main(p):

    t0 = time()
    print('start')
    print('start reading out and analyzing trodes')

########Read out and Analysis################

#Tetrode

    if p['probe_type'] == 'tetrode':
        for h in range(p['max_nr_of_tetrodes_per_shank']):
            for s in range(p['shanks']):
                print('########################  read tetrode {:g}{:g} ##############################'.format(h,s))
                tetrode_file = read_tetrode(h,s,p)
                if p['spikesorting']:
                    print('################################### generate tetrode {:g}{:g} prm and prb file ######################################################'.format(h,s))
                    create_tetrode_prm_file(h,s,p)
                    create_tetrode_prb_file(h,s,p)
                    print('############################# spikesorting, clustering of tetrode {:g}{:g} data ################################################'.format(h,s))
                    do_klusta(h,s,p)
                if p['LFP_analysis']:
                    read_evoked_lfp([h,s],p,tetrode_file)

        t2 = time()
        print('Effort to read and analyze tetrodes: ', t2-t0)

      ########### after first stage of manual clustering generate spikinfo pickle file #########
        """for h in range(p['shanks']):
            for s in range(p['max_nr_of_tetrodes_per_shank']):
                print('################################### generate spikeinfo pickle file for tetrode {:g}{:g}######################################################'.format(h,s))
                generate_spikeinfo_pickle(h,s,p)"""

#Linear

    elif p['probe_type'] == 'linear':
        for probe in range(p['probes']):
            for s in range(p['shanks']):
                print('########################  read probe {:g} shank {:g} ##############################'.format(probe,s))
                shank_file = read_linear(probe,s,p)
                if p['spikeSorting']:
                    print('################################### generate probe {:g} shank {:g} prm and prb file ######################################################'.format(probe,s))
                    create_shank_prm_file(probe,s,p)
                    create_shank_prb_file(probe,s,p)
                    print('############################# spikesorting, clustering of probe {:g} shank {:g} data ################################################'.format(probe,s))
                    do_klusta_for_shank(probe,s,p)
                if p['LFP_analysis']:
                    read_evoked_lfp([probe,s],p,shank_file)

        #generate_spikeinfo_pickle_for_shank(s,p)

#Polytrode

#if p['probe_type'] == 'poly':

####read out shank #####

#print 'start reading out shanks'
#shank_file, time_file = read_shank(0,p)
#shank_file_sp = shank_file.transpose().round().astype('int16')
#shank_file_sp.tofile('shank_ldopa_{:g}.dat'.format(0))
#print 'shank_ldopa_{:g}'.format(0)
#t2 = time()
#print "Effort to read shank: ", t2-t1

#print 'start reading out shanks'
#save_shank_to_dat(0,p)
#t2 = time()
#print "Effort to read shank: ", t2-t1


#probe_file, time_file = read_probe(p)

### generate .dat file for klusta spikedetekt

#tetrode_file_sp = tetrode_file.reshape(tetrode_file.shape[1],tetrode_file.shape[0]).flatten()

#tetrode_file_sp.astype('int16').tofile('first_experiment.dat')
