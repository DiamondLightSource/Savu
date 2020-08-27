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
            description: Sigma of the Gaussian window. Used to separate the
              low-pass and high-pass components of each sinogram column.
            default: 3
        size:
            visibility: intermediate
            dtype: int
            description:  Size of the median filter window. Used to
              clean stripes.
            default: 31
        """


    def get_citation(self):
        """
        citation1:
            description: The code of ring removal is the implementation of the work of
              Nghia T. Vo et al. taken from algorithm 2 and 3 in this paper
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