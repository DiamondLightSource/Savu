from savu.plugins.plugin_tools import PluginTools

class RemoveUnresponsiveAndFluctuatingRingsTools(PluginTools):
    """Method to remove large stripe artefacts in a sinogram (<-> ring
artefacts in a reconstructed image).
    """
    def define_parameters(self):
        """
        size:
            visibility: intermediate
            dtype: int
            description: Size of the median filter window. Greater is stronger
            default: 71
        snr:
            visibility: intermediate
            dtype: int
            description: Ratio used to detect locations of large stripes.
              Greater is less sensitive.
            default: 3.0
        """

    def get_bibtex(self):
        """@article{vo2018superior,
        title = {Superior techniques for eliminating ring artifacts in X-ray micro-tomography},
        author={Vo, Nghia T and Atwood, Robert C and Drakopoulos, Michael},
        journal={Optics express},
        volume={26},
        number={22},
        pages={28396--28412},
        year={2018},
        publisher={Optical Society of America}}
        """
