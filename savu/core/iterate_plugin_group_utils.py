from savu.data.data_structures.plugin_data import PluginData


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

            try:
                max_frames = plugin.get_max_frames()
            except AttributeError:
                # the plugin has no get_max_frames() method, so assume it to be
                # 'single
                max_frames = 'single'

            out_dataset[0].create_dataset(in_dataset[0])

            # create the cloned dataset
            create_clone(out_dataset[1], out_dataset[0])

            # this is the pattern that was used for the "original" output data
            # for the end plugin
            out_pattern = out_pData[0].get_pattern_name()
            # set the pattern for the PluginData objects associated with the
            # newly created cloned dataset
            out_pData[1].plugin_data_setup(out_pattern, max_frames)

            try:
                iterate_plugin_group = check_if_in_iterative_loop(plugin.exp)
                start_plugin = iterate_plugin_group.start_plugin
                start_plugin_in_pData, start_plugin_out_pData = \
                    start_plugin.get_plugin_datasets()
                # this is the pattern that was used for the input data for the
                # start plugin
                in_pattern = start_plugin_in_pData[0].get_pattern_name()

                # create PluginData object for original and cloned Data objects,
                # that have the pattern of the start plugin, and append to the
                # start plugin's 'plugin_in_datasets'
                orig_start_pData = PluginData(out_dataset[0], start_plugin)
                orig_start_pData.plugin_data_setup(in_pattern, 'single')
                start_plugin.parameters['plugin_in_datasets'].append(orig_start_pData)
                clone_start_pData = PluginData(out_dataset[1], start_plugin)
                clone_start_pData.plugin_data_setup(in_pattern, 'single')
                start_plugin.parameters['plugin_in_datasets'].append(clone_start_pData)
                # "re-finalise" the plugin datasets for the start plugin, now
                # that these new PluginData obejcts have been added
                start_plugin._finalise_plugin_datasets()
            except AttributeError as e:
                print('In plugin setup, will not create new PluginData objects')

    return wrapper

def setup_extra_plugin_data_padding(padding_fn):
    """
    Decorator that can be applied to a filter plugin's set_filter_padding()
    method. Doing so modifies/extends the filter plugin's padding function
    slightly to also set the padding for the additional PluginData objects that
    are created when an iterative loop is defined.
    """

    def wrapper(*args, **kwargs):
        # run the plugin's original set_filter_padding() method
        padding_fn(*args, **kwargs)
        plugin = args[0]

        if check_if_end_plugin_in_iterate_group(plugin.exp):
            # check for any padding on the original output data, and apply it to
            # the cloned data
            in_pData, out_pData = plugin.get_plugin_datasets()
            if out_pData[0].padding is not None:
                out_pData[1].padding = out_pData[0].padding

        try:
            iterate_plugin_group = check_if_in_iterative_loop(plugin.exp)
            in_pData, out_pData = plugin.get_plugin_datasets()
            start_plugin_in_pData, start_plugin_out_pData = \
                iterate_plugin_group.start_plugin.get_plugin_datasets()
            padding = out_pData[0].padding
            for plugin_data in start_plugin_in_pData:
                if plugin_data.padding is None:
                    plugin_data.padding = padding

            iterate_plugin_group.start_plugin._finalise_plugin_datasets()
        except AttributeError as e:
            print('In plugin setup, will not create new PluginData objects')
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
        start_index = shift_plugin_index(exp, group.start_index)
        end_index = shift_plugin_index(exp, group.end_index)
        if start_index <= current_plugin_index and \
            end_index >= current_plugin_index:
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

    end_index = shift_plugin_index(exp, iterate_plugin_group.end_index)
    is_end_plugin = end_index == exp.meta_data.get('nPlugin')

    return is_end_plugin

def shift_plugin_index(exp, index):
    '''
    The indices used for plugins when editing a process list in the
    configurator, and the indices used by PluginRunner._run_plugin_list(),
    differ based on a few different things, such as:
    - zero-based indexing internally in Savu, but one-based indexing in the
      configurator
    - the number of loaders in the process list

    This function is for shifting the one-based plugin index as would be seen in
    the configurator, to the nPlugin experimental metadata value as would be
    seen for the same plugin in the for loop in PluginRunner._run_plugin_list().
    '''
    n_loaders = exp.meta_data.plugin_list._get_n_loaders()
    SHIFT_TO_ZERO_BASED = 1
    return index - SHIFT_TO_ZERO_BASED - n_loaders