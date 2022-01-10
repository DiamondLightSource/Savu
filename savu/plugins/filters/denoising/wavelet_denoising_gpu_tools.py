from savu.plugins.plugin_tools import PluginTools

class WaveletDenoisingGpuTools(PluginTools):
    """A Wrapper for pypwt package for wavelet GPU denoising.
    """
    def define_parameters(self):
        """
        family_name:
             visibility: intermediate
             dtype: str
             options: [db3, db5, db7, db9, db11, haar, sym3, sym5, sym7, sym11]
             description: Wavelet family.
             default: db5

        nlevels:
             visibility: intermediate
             dtype: int
             description: Level of refinement for filter coefficients.
             default: 3

        threshold_level:
             visibility: basic
             dtype: float
             description: 
                summary: Threshold level to filter wavelet coefficients
                verbose: Smaller values lead to more smoothing
             default: 0.01

        pattern:
             visibility: intermediate
             dtype: str
             description: Pattern to apply this to.
             default: 'PROJECTION'

        """


    def citation(self):
        """
        PDWT (Parallel Discrete Wavelets Transform) is a Cuda-C++ 
        library for computing the discrete wavelets transform of 
        signal and images. Designed to be flexible and efficient, 
        it offers many built-in filters and features like thresholding.
        Its results are compatible with other wavelets software 
        like Matlab wavelets toolbox and Python package pywavelets.

        bibtex:
                @article{paleo_pdwt_2020,
                title={PDWT: Release 0.8},
                author={Pierre Paleo},
                journal={Zenodo},
                volume={},
                pages={},
                year={2020},
                publisher={Zenodo}
                }
        endnote:
                %0 Journal Article
                %T PDWT: Release 0.8
                %A Paleo, Pierre
                %J Zenodo
                %D 2020
                %I Zenodo
        doi: "10.5281/zenodo.4084182"
        """
