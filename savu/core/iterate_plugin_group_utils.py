def setup_iterative_plugin_out_datasets(in_dataset, out_dataset, in_pData,
                                        out_pData, patterns, max_frames):
    '''
    Run this method instead of the setup() method in a plugin that is
    - inside a group of plugins to iterate over
    - the END plugin in the group of plugins to iterate over

    Setup the output datasets and output plugin datasets to work with the cloned
    dataset that exists for "end plugins".
    '''
    # set the pattern for the single input dataset
    in_pData[0].plugin_data_setup(patterns['plugin_in_dataset'], max_frames)
    out_dataset[0].create_dataset(in_dataset[0])

    # create the cloned dataset
    create_clone(out_dataset[1], out_dataset[0])

    # set the pattern for the PluginData objects associated with the two
    # ouptut datasets (original and clone)
    out_pData[0].plugin_data_setup(patterns['plugin_out_datasets'], max_frames)
    out_pData[1].plugin_data_setup(patterns['plugin_out_datasets'], max_frames)

def create_clone(clone, data):
    '''
    Create a clone of a Data object
    '''
    clone.create_dataset(data)
    clone.data_info.set('clone', data.get_name())