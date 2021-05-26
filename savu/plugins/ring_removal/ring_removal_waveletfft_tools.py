from savu.plugins.plugin_tools import PluginTools

class RingRemovalWaveletfftTools(PluginTools):
    """Ring artefact removal method
    """
    def define_parameters(self):
        """
        nvalue:
            visibility: intermediate
            dtype: int
            description: Order of the the Daubechies (DB) wavelets.
            default: 5
        sigma:
            visibility: intermediate
            dtype: int
            description: Damping parameter. Larger is stronger.
            default: 1
        level:
            visibility: intermediate
            dtype: int
            description: Wavelet decomposition level.
            default: 3
        padFT:
            visibility: intermediate
            dtype: int
            description: Padding for Fourier transform
            default: 20
        """
