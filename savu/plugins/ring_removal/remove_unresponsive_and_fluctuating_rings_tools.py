from savu.plugins.plugin_tools import PluginTools


class RemoveUnresponsiveAndFluctuatingRingsTools(PluginTools):
    """Method working in the sinogram space to remove ring artifacts caused by
    dead pixels.
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
            description: Ratio used to detect locations of large stripes.
              Greater is less sensitive.
            default: 3.0
        residual:
            visibility: intermediate
            dtype: bool
            description: Removing residual stripes if True.
            default: True
        """

    def citation(self):
        """
        The code of ring removal is the implementation of the work of Nghia T.
        Vo et al. taken from algorithm 4, 5, 6 in this paper.
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
