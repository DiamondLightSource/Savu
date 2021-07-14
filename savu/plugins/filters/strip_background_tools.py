from savu.plugins.plugin_tools import PluginTools

class StripBackgroundTools(PluginTools):
    """1D background removal. PyMca magic function

    """
    def define_parameters(self):
        """
        iterations:
              visibility: basic
              dtype: int
              description: Number of iterations.
              default: 100
        window:
              visibility: basic
              dtype: int
              description: Half width of the rolling window.
              default: 10
        SG_filter_iterations:
              visibility: intermediate
              dtype: int
              description: How many iterations until smoothing occurs.
              default: 5
        SG_width:
              visibility: intermediate
              dtype: int
              description: Whats the savitzgy golay window.
              default: 35
        SG_polyorder:
              visibility: intermediate
              dtype: int
              description: Whats the savitzgy-golay poly order.
              default: 5
        out_datasets:
              visibility: datasets
              dtype: [list[],list[str]]
              description: 'A list of the dataset(s) to process.'
              default: ['in_datasets[0]','background']

        """
