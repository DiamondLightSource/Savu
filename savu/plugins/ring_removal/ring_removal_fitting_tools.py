from savu.plugins.plugin_tools import PluginTools

class RingRemovalFittingTools(PluginTools):
    """Method to remove stripe artefacts in a sinogram (<-> ring
artefacts in a reconstructed image) using a fitting-based method.
It's suitable for use on low-contrast sinogram and/or for removing
blurry rings.
    """
    def define_parameters(self):
        """
        sigmax:
            visibility: intermediate
            dtype: int
            description: Sigma of the Gaussian window in x-direction which\
              controls the strength of the removal.
            default: 5
        sigmay:
            visibility: intermediate
            dtype: int
            description: Sigma of the Gaussian window in y-direction
            default: 20
        order:
            visibility: intermediate
            dtype: int
            description: polynomial fit order.
            default: 2
        """

    def get_citation(self):
        """
        citation1:
            description: The code of ring removal is the implementation of the work of
              Nghia T. Vo et al. taken from algorithm 1 in this paper
            bibtex: |
                    @article{vo2018superior,
                    title = {Superior techniques for eliminating ring artifacts in X-ray micro-tomography},
                    author={Vo, Nghia T and Atwood, Robert C and Drakopoulos, Michael},
                    journal={Optics express},
                    volume={26},
                    number={22},
                    pages={28396--28412},
                    year={2018},
                    publisher={Optical Society of America}}
            endnote: |
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