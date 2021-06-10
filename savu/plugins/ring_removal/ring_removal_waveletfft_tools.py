from savu.plugins.plugin_tools import PluginTools

class RingRemovalWaveletfftTools(PluginTools):
    """Wavelet-FFt-based method working in the sinogram space to remove ring
    artifacts.
    """
    def define_parameters(self):
        """
        sigma:
            visibility: basic
            dtype: int
            description: Damping parameter. Larger is stronger.
            default: 1
        level:
            visibility: basic
            dtype: int
            description: Wavelet decomposition level.
            default: 4
        nvalue:
            visibility: intermediate
            dtype: int
            description: Order of the the Daubechies (DB) wavelets.
            default: 8
        padFT:
            visibility: intermediate
            dtype: int
            description: Padding for Fourier transform
            default: 20
        """
