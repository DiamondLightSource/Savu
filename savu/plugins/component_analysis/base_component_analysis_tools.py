from savu.plugins.plugin_tools import PluginTools

class BaseComponentAnalysisTools(PluginTools):
    """
    A base plugin for doing component analysis. This sorts out the main
    features of a component analysis
    """

    def define_parameters(self):
        """
        out_datasets:
            visibility: datasets
            dtype: [list[],list[str]]
            description: "A list of the dataset(s) to process."
            default: "['scores', 'eigenvectors']"

        number_of_components:
            visibility: basic
            dtype: int
            description: The number of expected components.
            default: 3

        chunk:
            visibility: intermediate
            dtype: str
            description: The chunk to work on
            default: 'SINOGRAM'

        whiten:
            visibility: intermediate
            dtype: int
            description: To subtract the mean or not.
            default: 1

        """