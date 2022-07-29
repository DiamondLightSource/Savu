from savu.plugins.plugin_tools import PluginTools

class DetectStripesTools(PluginTools):
    """
    A plugin to detect stripes in a sinogram and return a 2D binary mask that
    specifies the position of the stripes.
    """
    def define_parameters(self):
        """
        size:
            visibility: basic
            dtype: int
            description: Size of the median filter window. Greater is stronger.
            default: 51
        snr:
            visibility: basic
            dtype: float
            description: Ratio used to detect locations of stripes.
              Greater is less sensitive.
            default: 3.0

        binary_dilation:
            visibility: basic
            dtype: bool
            description: Apply binary dilation to the stripe mask
            default: True
        """

    def citation(self):
        """
        The code of stripe artifact detection is the implementation of the work
        of Nghia T. Vo et al. taken from algorithm 4 in this paper.
        bibtex:
                @article{vo2018superior,
                title = {Superior techniques for eliminating ring artifacts in X-ray micro-tomography},
                author={Vo, Nghia T and Atwood, Robert C and Drakopoulos, Michael},
                journal={Optics express},
                volume={26},
                number={22},
                pages={28396--28412},
                year={2018},
                publisher={Optical Society of America}}
        endnote:
                %0 Journal Article
                %T Superior techniques for eliminating ring artifacts in X-ray micro-tomography
                %A Vo, Nghia T
                %A Atwood, Robert C
                %A Drakopoulos, Michael
                %J Optics express
                %V 26
                %N 22
                %P 28396-28412
                %@ 1094-4087
                %D 2018
                %I Optical Society of America
        doi: "10.1364/OE.26.028396"
        """
