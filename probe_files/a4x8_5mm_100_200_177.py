import numpy as np
probe_info = {}
probe_info['numShanks'] = 4
probe_info['type'] = 'linear'
probe_info['numTrodesPerShank'] = 8
probe_info['numTrodes'] = 32

probe_info['bottom_ycoord'] = 0
probe_info['top_ycoord'] = 800

###Channel mapping###
neuronexus_to_intan = [15,5,4,14,3,6,2,7,1,8,0,9,13,12,11,10,21,20,19,18,22,24,23,17,25,16,26,28,27,30,29,31]
id = np.zeros((probe_info['numShanks'], probe_info['numTrodesPerShank']))
for i in range(probe_info['numShanks']):
    id[i,:] = [neuronexus_to_intan[0+i*8], neuronexus_to_intan[7+i*8], neuronexus_to_intan[1+i*8], neuronexus_to_intan[6+i*8], neuronexus_to_intan[2+i*8], neuronexus_to_intan[5+i*8], neuronexus_to_intan[3+i*8], neuronexus_to_intan[4+i*8]]

probe_info['id'] = id
