def enable_iterative_loop(setup_fn):
    '''
    Decorator that can be applied to a plugin's setup() method. Doing so
    modifies the plugin's setup slightly to work correctly when at the end of an
    iterative loop, by setting up the relevant extra output dataset.
    '''
    def wrapper(*args, **kwargs):
        # run the plugin's original setup() method
        setup_fn(*args, **kwargs)
        plugin = args[0]

        if check_if_end_plugin_in_iterate_group(plugin.exp):
            # do the other setup required for the plugin to be the end plugin of
            # an iterative group

            in_dataset, out_dataset = plugin.get_datasets()
            in_pData, out_pData = plugin.get_plugin_datasets()

            patterns = {
                'plugin_in_dataset': plugin.parameters['pattern'],
                'plugin_out_datasets': plugin.parameters['pattern']
            }

            max_frames = plugin.get_max_frames()

            # set the pattern for the single input dataset
            in_pData[0].plugin_data_setup(patterns['plugin_in_dataset'],
                max_frames)
            out_dataset[0].create_dataset(in_dataset[0])

            # create the cloned dataset
            create_clone(out_dataset[1], out_dataset[0])

            # set the pattern for the PluginData objects associated with the two
            # output datasets (original and clone)
            out_pData[0].plugin_data_setup(patterns['plugin_out_datasets'],
                max_frames)
            out_pData[1].plugin_data_setup(patterns['plugin_out_datasets'],
                max_frames)

    return wrapper

def create_clone(clone, data):
    '''
    Create a clone of a Data object
    '''
    clone.create_dataset(data)
    clone.data_info.set('clone', data.get_name())

def check_if_in_iterative_loop(exp):
    '''
    Inspect the metadata inside the Experiment object to determine if current
    processing is inside an iterative loop
    '''
    current_plugin_index = exp.meta_data.get('nPlugin')
    for group in exp.meta_data.get('iterate_groups'):
        if group['start_plugin_index'] <= current_plugin_index and \
            group['end_plugin_index'] >= current_plugin_index:
            return group

    # never hit an instance of IteratePluginGroup where the current plugin
    # index was within the start and end plugin indices, so processing is
    # not inside an iterative loop
    return None

def check_if_end_plugin_in_iterate_group(exp):
    '''
    Determines if the current plugin is at the end of an iterative loop
    '''
    iterate_plugin_group = check_if_in_iterative_loop(exp)
    if iterate_plugin_group is None:
        return False

    is_end_plugin = \
        iterate_plugin_group['end_plugin_index'] == exp.meta_data.get('nPlugin')

    return is_end_plugin