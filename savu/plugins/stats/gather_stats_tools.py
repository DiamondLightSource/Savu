from savu.plugins.plugin_tools import PluginTools

class GatherStatsTools(PluginTools):
    """(Change this) A short description of the plugin"""
    
    def define_parameters(self):
        """
        pattern:
            visibility: intermediate
            dtype: str
            description: "Describe your parameter"
            default: PROJECTION
            options: [PROJECTION, SINOGRAM, VOLUME_XZ]
        """

    #def citation1(self):
        #"""
        #A description of the citation
        #bibtex:
        #        A bibtex string.
        #endnote:
        #        An endnote string.
        #doi: A link in the form of numbers and letters
        #dependency:
        #    parameter_name_2: The name of the method for which this citation is for
        #"""