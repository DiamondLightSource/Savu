from savu.plugins.plugin_tools import PluginTools
from savu.plugins.utils import register_plugin_tool

@register_plugin_tool
class BaseReconTools(PluginTools):
    """A base class for reconstruction plugins
    """
    def define_parameters(self):
        """
        centre_of_rotation:
             visibility: advanced
             dtype: float
             description: Centre of rotation to use for the
               reconstruction.
             default: 0.0
        init_vol:
             visibility: advanced
             dtype: float
             description: Dataset to use as volume initialiser
               (doesn't currently work with preview)
             default: 'None'
        centre_pad:
             visibility: basic
             dtype: float
             description: Pad the sinogram to centre it in order
               to fill the reconstructed volume ROI for asthetic
               purposes.
             warning: This will significantly increase the size of
               the data and the time to compute the reconstruction)
               Only available for selected algorithms and will be
               ignored otherwise.
             default: false
             dependency:
               algorithm: [FP_CUDA, FBP_CUDA, BP_CUDA, FP, FBP, BP]
        outer_pad:
             visibility: basic
             dtype: float
             description: Pad the sinogram width to fill the
               reconstructed volume for asthetic purposes. Choose
               from True (defaults to sqrt(2)), False or
               float <= 2.1.
             warning: This will increase the size of the data and
               the time to compute the reconstruction. Only available
               for selected algorithms and will be ignored otherwise.
             default: false
             dependency:
               algorithm: [FP_CUDA, FBP_CUDA, BP_CUDA, FP, FBP, BP]
        log:
             visibility: advanced
             dtype: bool
             description:
              summary: Take the log of the data before reconstruction
                (true or false).
              verbose: Should be set to false if PaganinFilter is
                set beforehand
             default: true
        preview:
             visibility: advanced
             dtype: list
             description: A slice list of required frames.
             default: '[]'
        force_zero:
             visibility: basic
             dtype: range
             description: Set any values in the reconstructed image
               outside of this range to zero.
             default: 'None, None'
        ratio:
             visibility: basic
             dtype: float
             description: Ratio of the masks diameter in pixels to
               the smallest edge size along given axis.
             default: 0.95
        log_func:
             visibility: basic
             dtype: int
             description: Override the default log function
             default: np.nan_to_num(-np.log(sino))
        vol_shape:
             visibility: basic
             dtype: str
             description: Override the size of the reconstuction
               volume with an integer value.
             default: fixed

        """

    def get_bibtex(self):
        """@article{baserecon2009fast,
         title={A fast iterative shrinkage-thresholding algorithm for linear inverse problems},
         author={Beck, Amir and Teboulle, Marc},
         journal={SIAM journal on imaging sciences},
         volume={2},
         number={1},
         pages={183--202},
         year={2009},
         publisher={SIAM}
        }
        """

