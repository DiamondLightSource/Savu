from savu.plugins.plugin_tools import PluginTools

class RingRemovalFilteringTools(PluginTools):
    """Method to remove stripe artefacts in a sinogram (<-> ring
artefacts in a reconstructed image) using a filtering-based
method in the combination with a sorting-based method.
Note that it's different to a FFT-based or wavelet-FFT-based
method.
    """
    def define_parameters(self):
        """
        sigma:
            visibility: intermediate
            dtype: int
            description: Sigma of the Gaussian window. Used to separate the\
              low-pass and high-pass components of each sinogram column.
            default: 3
        size:
            visibility: intermediate
            dtype: int
            description:  Size of the median filter window. Used to\
              clean stripes.
            default: 31
        """

    def get_bibtex(self):
        r"""@article{vo2018superior,
            title = {Superior techniques for eliminating ring artifacts in X-ray micro-tomography},
            author={Vo, Nghia T and Atwood, Robert C and Drakopoulos, Michael},
            journal={Optics express},
            volume={26},
            number={22},
            pages={28396--28412},
            year={2018},
            publisher={Optical Society of America}
            }
        """
