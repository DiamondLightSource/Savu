from savu.plugins.plugin_tools import PluginTools

class BaseAstraVectorReconTools(PluginTools):
    """A Plugin to perform Astra toolbox reconstruction using vector
geometry
    """
    def define_parameters(self):
        """
        n_iterations:
            visibility: basic
            dtype: int
            description: Number of Iterations is only valid for iterative algorithms
            default: 1
            dependency:
              algorithm: [SIRT_CUDA, SART_CUDA, CGLS_CUDA]

        """
