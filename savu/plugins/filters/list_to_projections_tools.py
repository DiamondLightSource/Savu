from savu.plugins.plugin_tools import PluginTools

class ListToProjectionsTools(PluginTools):
    """Convert a list of points into a 2D projection
    """
    def define_parameters(self):
        """
        step_size_x:
              visibility: basic
              dtype: [None,float]
              description: step size in the interp, None if minimum chosen.
              default: None
        step_size_y:
              visibility: basic
              dtype: [None,float]
              description: step size in the interp, None if minimum chosen.
              default: None
        fill_value:
              visibility: basic
              dtype: [int, str, float]
              description: The value to fill with, takes an average if nothing
               else chosen.
              default: 'mean'
        """