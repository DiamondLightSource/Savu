from savu.plugins.plugin_tools import PluginTools

class DenoiseBregmanFilterTools(PluginTools):
    """Split Bregman method for solving the denoising Total Variation ROF model.
    """
    def define_parameters(self):
        """
        weight:
             visibility: basic
             dtype: float
             description: 'Denoising factor.'
             default: 2.0

        max_iterations:
             visibility: basic
             dtype: int
             description: "Total number of regularisation iterations.
               The smaller the number of iterations, the smaller the effect
               of the filtering is. A larger number will affect the speed
               of the algorithm."
             default: 30

        error_threshold:
             visibility: advanced
             dtype: float
             description: Convergence threshold.
             default: 0.001

        isotropic:
             visibility: advanced
             dtype: [bool, str]
             description: Isotropic or Anisotropic filtering.
             options: [Isotropic, Anisotropic]
             default: False

        """