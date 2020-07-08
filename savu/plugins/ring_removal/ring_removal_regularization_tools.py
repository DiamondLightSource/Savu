from savu.plugins.plugin_tools import PluginTools

class RingRemovalRegularizationTools(PluginTools):
    """Method to remove stripe artefacts in a sinogram (<-> ring
artefacts in a reconstructed image) using a regularization-based
method. A simple improvement to handle partial stripes is included.
    """
    def define_parameters(self):
        """
        alpha:
            visibility: intermediate
            dtype: float
            description: The correction strength. Smaller is stronger.
            default: 0.005
        number_of_chunks:
            visibility: intermediate
            dtype: int
            description: Divide the sinogram to many chunks of rows.
            default: 1
        """

