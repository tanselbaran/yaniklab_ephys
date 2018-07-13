from glob import glob
from probe_classes import *
import importlib

class Experiment:
    def createProbe(self, probe_name):
        probe_module = importlib.import_module('probe_files.'+probe_name)
        probe_info = probe_module.probe_info
        probe_type = probe_info['type']
        if probe_type == 'tetrode':
            self.probe = tetrode(probe_name)
        elif probe_type == 'linear':
            self.probe = linear(probe_name)
        elif probe_type == 'array':
            self.probe = array(probe_name)
        else:
            raise ValueError('Invalid probe type.')

    def get_input_for_pref(self,statement):
        while True:
            inpt = input(statement)
            if (inpt == 'y' or inpt == 'n'):
                break
            else:
                print("Invalid input! Please enter a valid input (y or n).")
        return inpt


class Session:
    def __init__(self, session_name, subExperiment):
        self.name = session_name
        self.dir = subExperiment.dir + '/' + session_name
        self.subExperiment = subExperiment

    def get_input_for_pref(self,statement):
        while True:
            inpt = input(statement)
            if (inpt == 'y' or inpt == 'n'):
                break
            else:
                print("Invalid input! Please enter a valid input (y or n).")
        return inpt

    def set_analysis_preferences(self):
        preferences = {}
        print(self.name)
        preferences['do_whisker_stim_evoked'] = self.get_input_for_pref("Do whisker stimulation evoked analysis for this session? (y/n)")
        preferences['do_optical_stim_evoked'] = self.get_input_for_pref("Do optical stimulation evoked analysis for this session? (y/n)")
        preferences['do_electrical_stim_evoked'] = self.get_input_for_pref("Do electrical stimulation evoked analysis for this session? (y/n)")
        preferences["do_spectogram_analysis"] = self.get_input_for_pref("Do spectogram analysis on low frequency LFP for this session? (y/n)")
        self.preferences = preferences

    def set_amplifier(self):
        info_file = glob(self.dir + '/info*')[0]
        info_file_suffix = info_file.split('.')[-1]
        self.amplifier = info_file_suffix

    def setTrigChannels(self, *args):
        self.set_amplifier()
        if self.amplifier == 'rhd':
            prefix = 'board-DIN-0'
        elif self.amplifier == 'rhs':
            prefix = 'board-DIGITAL-IN-0'
        if self.preferences['do_whisker_stim_evoked'] == 'y':
            self.whisker_stim_channel = self.dir + '/' + prefix + str(args[0]) + '.dat'
        if self.preferences['do_optical_stim_evoked'] == 'y':
            self.optical_stim_channel = self.dir + '/' + prefix + str(args[1]) + '.dat'
        if self.preferences['do_electrical_stim_evoked'] == 'y':
            #TO BE FILLED
            pass

class acute(Experiment):

    def __init__(self, experiment_dir):
        self.dir = experiment_dir
        self.locations = {}

    def add_location(self, location_dir):
        index_location = len(self.locations)
        self.locations[index_location] = Location(location_dir, self)
        print(location_dir)
        self.locations[index_location].amplifier_port = input('Please enter the amplifier port to which the amplifier is connected to')
        preferences = {}
        preferences['do_spike_analysis'] = self.get_input_for_pref("Do spike detection, sorting and post-processing for this session? (y/n)")
        self.locations[index_location].preferences = preferences

class subExperiment:
    def __init__(self, location_dir, experiment):
        self.dir = location_dir
        self.sessions = {}
        self.experiment = experiment

    def add_session(self, session_name, order):
        index_session = len(self.sessions)
        self.sessions[index_session] = Session(session_name, self)
        self.sessions[index_session].set_analysis_preferences()
        self.sessions[index_session].order = order

    def add_sessions_in_dir(self):
        subdirs = sorted(glob(self.dir + "/*"))
        for subdir in subdirs:
            current_session = 1
            session_name = subdir.split('/')[-1]
            if len(subdirs) == 1:
                order = 3
            elif current_session == 1:
                order = 0
            elif current_session == len(subdirs):
                order = 2
            else:
                order = 1
            self.add_session(session_name, order)
            current_session = current_session + 1


class chronic(Experiment):
    def __init__(self, experiment_dir):
        self.dir = experiment_dir
        self.days = {}

    def add_day(self, day_dir):
        index_day = len(self.days)
        self.days[index_day] = Day(day_dir, self)
        self.days[index_day].amplifier_port = input('Please enter the amplifier port to which the amplifier is connected to')

class Location(subExperiment):
    pass

class Day(subExperiment):
    pass
