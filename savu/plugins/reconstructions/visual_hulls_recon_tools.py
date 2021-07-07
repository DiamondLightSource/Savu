from savu.plugins.plugin_tools import PluginTools

class VisualHullsReconTools(PluginTools):
    """A Plugin to reconstruct an image by filter back projection
using the inverse radon transform from scikit-image.
    """
    def define_parameters(self):
        """
        threshold:
            visibility: basic
            dtype: float
            description: Threshold to binarize the input sinogram.
            default: 0.5

        init_vol:
            visibility: hidden
        """

    def citation(self):
        """
        The reconstruction performed in this processing
        chain is derived from this work
        bibtex:
                @article{laurentini1994visual,
                title={The visual hull concept for silhouette-based image understanding},
                author={Laurentini, Aldo},
                journal={IEEE Transactions on pattern analysis and machine intelligence},
                volume={16},
                number={2},
                pages={150--162},
                year={1994},
                publisher={IEEE}
                }
        endnote:
                %0 Journal Article
                %T The visual hull concept for silhouette-based image understanding
                %A Laurentini, Aldo
                %J IEEE Transactions on pattern analysis and machine intelligence
                %V 16
                %N 2
                %P 150-162
                %@ 0162-8828
                %D 1994
                %I IEEE
        doi: "http://dx.doi.org/10.1109/34.273735"
        """