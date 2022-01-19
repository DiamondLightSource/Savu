from savu.plugins.plugin_tools import PluginTools

class MrcSaverTools(PluginTools):
    """Plugin to save data as .mrc"""
    
    def define_parameters(self):
        """
        pattern:
            visibility: basic
            dtype: str
            description: How to slice the data
            default: VOLUME_XZ
        
        mrc_mode:
            visibility: basic
            dtype: str
            description: Bit depth (sets mrc_mode)
            default: 'uint16'
            options: ['int8', 'int16', 'float32', 'complex64', 'uint16']
        """
