from savu.plugins.plugin_tools import PluginTools

class UmpaTools(PluginTools):
    """A plugin to perform speckle tracking using the UMPA method
    """
    def define_parameters(self):
        """
        in_datasets:
              visibility: datasets
              dtype: [list[],list[str]]
              description: 'A list of the dataset(s) to process.'
              default: ['signal','reference']
        out_datasets:
              visibility: datasets
              dtype: [list[],list[str]]
              description: 'A list of the dataset(s) output.'
              default: ['T','dx','dy','df','f']
        Nw:
              visibility: basic
              dtype: int
              description: '2*Nw + 1 is the width of the window.'
              default: 4
        step:
              visibility: basic
              dtype: int
              description: 'Perform the analysis on every other
                _step_ pixels in both directions. '
              default: 1
        max_shift:
              visibility: basic
              dtype: int
              description: Do not allow shifts larger than this number of pixels.
              default: 4

        """