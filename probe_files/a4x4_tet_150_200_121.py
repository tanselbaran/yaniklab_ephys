import numpy as np
probe_info['numShanks'] = 4
probe_info['type'] = 'tetrode'
probe_info['numTetrodes'] = 16
probe_info['numTetrodesPerShank'] = 4

###Channel mapping###
neuronexus_to_intan=[17,21,42,25,38,27,19,34,23,32,36,49,29,51,31,53,48,55,50,57,52,60,54,62,56,58,63,61,59,44,46,40,22,16,18,5,3,1,4,6,0,8,2,10,7,12,9,14,11,33,13,35,15,26,30,41,28,45,37,24,39,20,43,47]
id = np.zeros((probe_info['numTetrodes'],4))

height = 0
for tetrode in range(probe_info['numTetrodes']):
    if height == 0:
        id[tetrode,:] = [neuronexus_to_intan[0+i*16],neuronexus_to_intan[2+i*16],neuronexus_to_intan[15+i*16],neuronexus_to_intan[13+i*16]]
    elif height == 1:
        id[tetrode,:] = [neuronexus_to_intan[1+i*16],neuronexus_to_intan[4+i*16],neuronexus_to_intan[14+i*16],neuronexus_to_intan[10+i*16]]
    elif height == 2:
        id[tetrode,:] = [neuronexus_to_intan[3+i*16],neuronexus_to_intan[6+i*16],neuronexus_to_intan[12+i*16],neuronexus_to_intan[9+i*16]]
    elif height == 3:
        id[tetrode,:] = [neuronexus_to_intan[5+i*16],neuronexus_to_intan[7+i*16],neuronexus_to_intan[11+i*16],neuronexus_to_intan[8+i*16]]
        height = 0
probe_info['id'] = id
