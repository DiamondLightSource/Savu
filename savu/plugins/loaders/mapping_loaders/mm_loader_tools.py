from savu.plugins.plugin_tools import PluginTools


class MmLoaderTools(PluginTools):
    """
    Testing the mmloader plugin
    """
        
    def define_parameters(self):
        """
        dataset_names:
            visibility: basic
            dtype: list[str, str, str, str]
            description: The names assigned to each dataset in the order
              [fluorescence, diffraction, absorption, monitor]
            default: ['fluo', 'xrd', 'stxm', 'monitor']
        
        preview:
              visibility: basic
              dtype: [preview, dict{str: preview},dict{}]
              description: A slice list of required frames to apply to ALL 
                  datasets, else a dictionary of slice lists where the key is 
                  the dataset name.
              default: []
        """
