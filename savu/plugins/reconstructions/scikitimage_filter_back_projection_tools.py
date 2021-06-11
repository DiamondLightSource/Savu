from savu.plugins.plugin_tools import PluginTools

class ScikitimageFilterBackProjectionTools(PluginTools):
    """A Plugin to reconstruct an image by filter back projection using the
inverse radon transform from scikit-image.
    """

    def define_parameters(self):
        """
        output_size:
            visibility: intermediate
            dtype: [None, int,list[int,int],str]
            description: Integer number of rows and columns in the
                reconstruction, or 'auto'.
            default: auto

        filter:
            visibility: intermediate
            dtype: str
            description: Filter used in frequency domain filtering.
            options: [ramp, shepp-logan, cosine, hamming, hann, None]
            default: ramp

        interpolation:
            visibility: intermediate
            dtype: int
            description: Interpolation method used in reconstruction 
                ('cubic' option is slow)
            options: [linear,nearest,cubic]
            default: linear

        circle:
            visibility: intermediate
            dtype: bool
            description: Assume the reconstructed image is zero outside
              the inscribed circle. Also changes the default output_size
              to match the behaviour of radon called with circle=True.
            default: False

        vol_shape:
             visibility: hidden          
        """

    def citation(self):
        """
        The Tomographic reconstruction performed in this
        processing chain is derived from this work
        bibtex:
                @article{kak2002principles,
                title={Principles of computerized tomographic imaging},
                author={Kak, Avinash C and Slaney, Malcolm and Wang, Ge},
                journal={Medical Physics},
                volume={29},
                number={1},
                pages={107--107},
                year={2002},
                publisher={Wiley Online Library}
                }
        endnote:
                %0 Journal Article
                %T Principles of computerized tomographic imaging
                %A Kak, Avinash C
                %A Slaney, Malcolm
                %A Wang, Ge
                %J Medical Physics
                %V 29
                %N 1
                %P 107-107
                %@ 0094-2405
                %D 2002
                %I Wiley Online Library
        short_name_article: Principles of CT imaging
        doi: "https://doi.org/10.1137/1.9780898719277"


        """
