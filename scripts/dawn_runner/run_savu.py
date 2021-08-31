'''
run_savu
This is a refactor of the code that used to be contained in dawn.
It's used to mock up a runner for individual savu plugins from a python shell.
It is currently very early in development and will be subject to massive refactor in the future.
'''
from savu.data.experiment_collection import Experiment
from savu.data.meta_data import MetaData
from savu.plugins.utils import get_plugin
import savu.plugins.loaders.utils.yaml_utils as yaml
import os, sys
import numpy as np
from copy import deepcopy as copy
import time
from collections import OrderedDict


def get_output_rank(path2plugin, inputs, params, persistence):
    sys_path_0_lock = persistence['sys_path_0_lock']
    sys_path_0_lock.acquire()
    try:
        parameters = {}
        # slight repack here
        for key in list(params.keys()):
            val = params[key]["value"]
            if type(val)==type(''):
                val = val.replace('\n','').strip()
                parameters[key] = val
        plugin = _savu_setup(path2plugin, inputs, parameters)
        persistence['plugin_object'] = plugin
    finally:
        sys_path_0_lock.release()

    return len(plugin.get_plugin_out_datasets()[0].get_core_dimensions())


def runSavu(path2plugin, params, metaOnly, inputs, persistence):
    '''
    path2plugin  - is the path to the user script that should be run
    params - are the savu parameters
    metaOnly - a boolean for whether the data is kept in metadata or is passed as data
    inputs      - is a dictionary of input objects 
    '''
    t1 = time.time()
    sys_path_0_lock = persistence['sys_path_0_lock']
    sys_path_0_set = persistence['sys_path_0_set']
    plugin_object = persistence['plugin_object']
    axis_labels = persistence['axis_labels']
    axis_values = persistence['axis_values']
    string_key = persistence['string_key']
    parameters = persistence['parameters']
    aux = persistence['aux']
    sys_path_0_lock.acquire()
    try:
        result = copy(inputs)

        scriptDir = os.path.dirname(path2plugin)
        sys_path_0 = sys.path[0]
        if sys_path_0_set and scriptDir != sys_path_0:
            raise Exception("runSavu attempted to change sys.path[0] in a way that "
                            "could cause a race condition. Current sys.path[0] is {!r}, "
                            "trying to set to {!r}".format(sys_path_0, scriptDir))
        else:
            sys.path[0] = scriptDir
            sys_path_0_set = True
        
        if not plugin_object:
            parameters = {}
                # slight repack here
            for key in list(params.keys()):
#                 print "here"
                val = params[key]["value"]
                if type(val)==type(''):
                    val = val.replace('\n','').strip()
#                 print val
                parameters[key] = val
                print(("val: {}".format(val)))
#             print "initialising the object"
            plugin_object = _savu_setup(path2plugin, inputs, parameters)
            persistence['plugin_object'] = plugin_object
            axis_labels, axis_values = process_init(plugin_object)
#             print "I did the initialisation"
#             print "axis labels",axis_labels
#             print "axis_values", axis_values
#             print plugin_object
            chkstring =  [any(isinstance(ix, str) for ix in axis_values[label]) for label in axis_labels]
            if any(chkstring): # are any axis values strings we instead make this an aux out
                metaOnly = True
#                 print "AXIS LABELS"+str(axis_values)
                string_key = axis_labels[chkstring.index(True)]
                aux = OrderedDict.fromkeys(axis_values[string_key])
#                 print aux.keys()
            else:
                string_key = axis_labels[0]# will it always be the first one?
            if not metaOnly:
                if len(axis_labels) == 1:
                    result['xaxis']=axis_values[axis_labels[0]]
                    result['xaxis_title']=axis_labels[0]
                if len(axis_labels) == 2:
#                     print "set the output axes"
                    x = axis_labels[0]
                    result['xaxis_title']=x
                    y = axis_labels[1]
                    result['yaxis_title']=y
                    result['yaxis']=axis_values[y]
                    result['xaxis']=axis_values[x]
        else:
            pass
    finally:
        sys_path_0_lock.release()

    if plugin_object.get_max_frames()>1: # we need to get round this since we are frame independant
        data = np.expand_dims(inputs['data'], 0)
    else:
        data = inputs['data']

    print(("metaOnly: {}".format(metaOnly)))

    if not metaOnly: 

        out = plugin_object.process_frames([data])
#         print "ran the plugin"

        result['data'] = out
    elif metaOnly:
        result['data'] = inputs['data']
#         print type(result['data'])
        out_array = plugin_object.process_frames([inputs['data']])

#         print aux.keys()

        for k,key in enumerate(aux.keys()):
            aux[key]=np.array([out_array[k]])# wow really

        result['auxiliary'] = aux
    t2 = time.time()
    print("time to runSavu = "+str((t2-t1)))
    return result


def _savu_setup(path2plugin, inputs, parameters):
    print("running _savu_setup")
    parameters['in_datasets'] = [inputs['dataset_name']]
    parameters['out_datasets'] = [inputs['dataset_name']]
    plugin = get_plugin(path2plugin.split('.py')[0]+'.py')
    plugin.exp = setup_exp_and_data(inputs, inputs['data'], plugin)
    plugin.set_parameters(parameters)
    plugin._set_plugin_datasets()
    plugin.setup()
    return plugin


def process_init(plugin):
    axis_labels = plugin.get_out_datasets()[0].get_axis_label_keys()
    axis_labels.remove('idx')  # get the labels
    axis_values = {}
    plugin._clean_up()  # this copies the metadata!
    for label in axis_labels:
        axis_values[label] = plugin.get_out_datasets()[0].meta_data.get(label)
    plugin.base_pre_process()
    plugin.pre_process()
    return axis_labels, axis_values


def setup_exp_and_data(inputs, data, plugin):
    exp = DawnExperiment(get_options())
    data_obj = exp.create_data_object('in_data', inputs['dataset_name'])
    data_obj.data = None
    if len(inputs['data'].shape)==1:
#         print data.shape
        if inputs['xaxis_title'] is None or inputs['xaxis_title'].isspace():
            inputs['xaxis_title']='x'
            inputs['xaxis'] = np.arange(inputs['data'].shape[0])
        data_obj.set_axis_labels('idx.units', inputs['xaxis_title'] + '.units')
        data_obj.meta_data.set('idx', np.array([1]))
        data_obj.meta_data.set(str(inputs['xaxis_title']), inputs['xaxis'])
        data_obj.add_pattern(plugin.get_plugin_pattern(), core_dims=(1,), slice_dims=(0, ))
        data_obj.add_pattern('SINOGRAM', core_dims=(1,), slice_dims=(0, )) # good to add these two on too
        data_obj.add_pattern('PROJECTION', core_dims=(1,), slice_dims=(0, ))
    if len(inputs['data'].shape)==2:
        if inputs['xaxis_title'] is None  or inputs['xaxis_title'].isspace():
            print("set x")
            inputs['xaxis_title']='x'
            inputs['xaxis'] = np.arange(inputs['data'].shape[0])
        if inputs['yaxis_title'] is None or inputs['yaxis_title'].isspace():
            print("set y")
            inputs['yaxis_title']='y'
            size_y_axis = inputs['data'].shape[1]
            inputs['yaxis'] = np.arange(size_y_axis)
        
        data_obj.set_axis_labels('idx.units', inputs['xaxis_title'] + '.units', inputs['yaxis_title'] + '.units')
        data_obj.meta_data.set('idx', np.array([1]))
        data_obj.meta_data.set(str(inputs['xaxis_title']), inputs['xaxis'])
        data_obj.meta_data.set(str(inputs['yaxis_title']), inputs['yaxis'])
        data_obj.add_pattern(plugin.get_plugin_pattern(), core_dims=(1,2,), slice_dims=(0, ))
        data_obj.add_pattern('SINOGRAM', core_dims=(1,2,), slice_dims=(0, )) # good to add these two on too
        data_obj.add_pattern('PROJECTION', core_dims=(1,2,), slice_dims=(0, ))
   
    data_obj.set_shape((1, ) + data.shape) # need to add for now for slicing...
    data_obj.get_preview().set_preview([])
    return exp

class DawnExperiment(Experiment):
    def __init__(self, options):
        self.index={"in_data": {}, "out_data": {}, "mapping": {}}
        self.meta_data = MetaData(get_options())
        self.nxs_file = None

def get_options():
    options = {}
    options['dawn_runner'] = True
    options['transport'] = 'hdf5'
    options['process_names'] = 'CPU0'
    options['processes'] = 'CPU0'
    options['data_file'] = ''
    options['process_file'] = ''
    options['out_path'] = ''
    options['inter_path'] = ''
    options['log_path'] = ''
    options['run_type'] = ''
    options['verbose'] = 'True'
    options['system_params'] = _set_system_params()
    options['command'] = ''
    return options

def _set_system_params():
    # look in conda environment to see which version is being used
    savu_path = sys.modules['savu'].__path__[0]
    sys_files = os.path.join(
            os.path.dirname(savu_path), 'system_files')
    subdirs = os.listdir(sys_files)
    sys_folder = 'dls' if len(subdirs) > 1 else subdirs[0]
    fname = 'system_parameters.yml'
    sys_file = os.path.join(sys_files, sys_folder, fname)
    return yaml.read_yaml(sys_file)
