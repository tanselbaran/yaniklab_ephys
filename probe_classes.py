import importlib

class Probe:
    def __init__(self, probe_name):
        self.name = probe_name
        probe_module = importlib.import_module('probe_files.'+probe_name)
        probe_info = probe_module.probe_info
        self.type = probe_info['type']
        self.nr_of_electrodes = probe_info['numTrodes']
        self.id = probe_info['id']
        return probe_info

class tetrode(Probe):
    def __init__(self, probe_name):
        probe_info = Probe.__init__(self, probe_name)
        self.nr_of_tetrodes = probe_info['numTetrodes']
        self.nr_of_groups = probe_info['numTetrodes']
        self.shanks = probe_info['numShanks']

    nr_of_electrodes_per_group = 4

class linear(Probe):
    def __init__(self, probe_name):
        probe_info = Probe.__init__(self, probe_name)
        self.nr_of_electrodes_per_shank = probe_info['numTrodesPerShank']
        self.shanks = probe_info['numShanks']
        self.nr_of_groups = self.shanks
        self.nr_of_electrodes_per_group = self.nr_of_electrodes_per_shank
        self.bottom_ycoord = probe_info['bottom_ycoord']
        self.top_ycoord = probe_info['top_ycoord']

class array(Probe):
    def __init__(self, probe_name):
        probe_info = Probe.__init__(self, probe_name)
        self.nr_of_groups = probe_info['nr_of_groups']
        self.nr_of_electrodes_per_group = probe_info['nr_of_electrodes_per_group']
