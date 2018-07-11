import numpy as np
probe_info = {}
probe_info['numShanks'] = 2
probe_info['type'] = 'linear'
probe_info['numTrodesPerShank'] = 16
probe_info['numTrodes'] = 32

probe_info['bottom_ycoord'] = 0
probe_info['top_ycoord'] = 1600

###Channel mapping###
neuronexus_to_intan = [30,26,21,17,27,22,20,25,28,23,19,24,29,18,31,16,0,15,2,13,8,9,7,1,6,14,10,11,5,12,4,3]
id = np.zeros((probe_info['numTrodesPerShank'], probe_info['numShanks'],))
for i in range(probe_info['numShanks']):
    id[:,i] = [neuronexus_to_intan[0+i*16], neuronexus_to_intan[15+i*16], neuronexus_to_intan[1+i*16], neuronexus_to_intan[14+i*16], neuronexus_to_intan[2+i*16], neuronexus_to_intan[13+i*16], neuronexus_to_intan[3+i*16], neuronexus_to_intan[12+i*16], neuronexus_to_intan[4+i*16], neuronexus_to_intan[11+i*16], neuronexus_to_intan[5+i*16], neuronexus_to_intan[10+i*16], neuronexus_to_intan[6+i*16], neuronexus_to_intan[9+i*16], neuronexus_to_intan[7+i*16], neuronexus_to_intan[8+i*16]]
    probe_info['id'] = id
