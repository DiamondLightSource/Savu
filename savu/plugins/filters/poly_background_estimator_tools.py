from savu.plugins.plugin_tools import PluginTools

class PolyBackgroundEstimatorTools(PluginTools):
    """This plugin uses peakutils to find peaks in spectra. This is then metadata.
    """
    def define_parameters(self):
        """
        out_datasets:
              visibility: datasets
              dtype: [list[],list[str]]
              description: 'Create a list of the dataset(s). '
              default: ['Peaks']
        n:
              visibility: basic
              dtype: int
              description: max number of polys.
              default: 2
        MaxIterations:
              visibility: intermediate
              dtype: int
              description: max number of iterations.
              default: 12
        weights:
              visibility: intermediate
              dtype: [int, str, float, list]
              description: weightings to apply.
              default: '1/data'
        pvalue:
              visibility: intermediate
              dtype: float
              description: 'Ratio of variance between successive poly
                iterations.'
              default: 0.9

        """
