from savu.plugins.plugin_tools import PluginTools

class FresnelFilterTools(PluginTools):
    """A low-pass filter to improve the contrast of reconstructed images which
     is similar to the Paganin filter but can work on both sinograms and
     projections.
    """
    def define_parameters(self):
        """
        ratio:
              visibility: basic
              dtype: float
              description: Control the strength of the filter. Greater is stronger
              default: 100.0
        pattern:
              visibility: basic
              dtype: str
              description: Data processing pattern
              options: [PROJECTION, SINOGRAM]
              default: SINOGRAM
        apply_log:
              visibility: basic
              dtype: bool
              description: Apply the logarithm function to a sinogram before
               filtering.
              default: True
        """

    def citation(self):
        """
        "The code is the implementation of the work taken from the following
        paper:"
        bibtex:
                @article{Vo:21,
                title = {Data processing methods and data acquisition for samples larger than the field of view in parallel-beam tomography},
                author = {Nghia T. Vo and Robert C. Atwood and Michael Drakopoulos and Thomas Connolley},
                journal = {Opt. Express},
                number = {12},
                pages = {17849--17874},
                publisher = {OSA},
                volume = {29},
                month = {Jun},
                year = {2021},
                doi = {10.1364/OE.418448}}
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