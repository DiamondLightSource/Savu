from savu.plugins.plugin_tools import PluginTools

class ScikitimageSartTools(PluginTools):
    """A Plugin to reconstruct an image by filter back projection using the
inverse radon transform from scikit-image.
    """

    def define_parameters(self):
        """

        iterations:
            visibility: basic
            dtype: int
            description: Number of iterations in the reconstruction.
            default: 1

        output_size:
            visibility: basic
            dtype: [None, int, list[int,int]]
            description: Number of rows and columns in the reconstruction.
            default: None

        filter:
            visibility: intermediate
            dtype: str
            description: Filter used in frequency domain filtering. Ramp
              filter used by default. Assign None to use no filter.
            options: [ramp, shepp-logan, cosine, hamming, hann, None]
            default: ramp

        interpolation:
            visibility: advanced
            dtype: int
            description: "Interpolation method used in reconstruction.
              Methods available: linear, nearest, and cubic (cubic is slow)."
            options: [linear, nearest, cubic]
            default: linear

        circle:
            visibility: advanced
            dtype: bool
            description: "Assume the reconstructed image is zero outside
              the inscribed circle. Also changes the default output_size
              to match the behaviour of radon called with circle=True."
            default: False

        image:
           visibility: advanced
           dtype: [None,list]
           description:  "2D array, dtype=float, optional.  Image containing
             an initial reconstruction estimate. Shape of this array should
             be (radon_image.shape[0], radon_image.shape[0]). The default is
             a filter backprojection using scikit.image.iradon as 'result'."
           default: None

        projection_shifts:
            visibility: advanced
            dtype: [list, None]
            description: "1D array dtype = float Shift the projections
              contained in radon_image (the sinogram) by this many pixels
              before reconstructing the image. The ith value defines the
              shift of the ith column of radon_image."
            default: None

        clip:
            visibility: advanced
            dtype: [list,None]
            description: "length-2 sequence of floats. Force all values in
              the reconstructed tomogram to lie in the range [clip[0],
              clip[1]]."
            default: None

        relaxation:
            visibility: advanced
            dtype: [float,None]
            description: Float. Relaxation parameter for the update step. A
              higher value can improve the convergence rate, but one runs the risk
              of instabilities. Values close to or higher than 1 are not recommended.
            default: None

        outer_pad:
            visibility: hidden
            dtype: [bool,int,float]
            description: Not required.
            default: False

        centre_pad:
            visibility: hidden
            dtype: [bool,int,float]
            description: Not required.
            default: False

        """

    def citation(self):
        """
        The Tomographic reconstruction performed in this
        processing chain is derived from this work.
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
        doi: "https://doi.org/10.1137/1.9780898719277"
        """