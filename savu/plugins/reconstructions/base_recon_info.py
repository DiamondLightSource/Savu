# replaces base_recon.yaml
from savu.plugins.plugin_info import PluginInfo

class BaseReconInfo(PluginInfo):
    """
    .. module:: base_recon
       :platform: Unix
       :synopsis: A base class for all reconstruction methods
    .. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>
    """
    def define_parameters(self):
        """---
        centre_of_rotation:
             visibility: user
             type: float
             description: Centre of rotation to use for the
               reconstruction.
             default: 0.0
        init_vol:
             visibility: user
             type: float
             description: Dataset to use as volume initialiser
               (doesn't currently work with preview)
             default: 'None'
        centre_pad:
             visibility: param
             type: float
             description: Pad the sinogram to centre it in order
               to fill the reconstructed volume ROI for asthetic
               purposes.
             warning: This will significantly increase the size of
               the data and the time to compute the reconstruction)
               Only available for selected algorithms and will be
               ignored otherwise.
             default: false
        outer_pad:
             visibility: param
             type: float
             description: Pad the sinogram width to fill the
               reconstructed volume for asthetic purposes. Choose
               from True (defaults to sqrt(2)), False or
               float <= 2.1.
             warning: This will increase the size of the data and
               the time to compute the reconstruction. Only available
               for selected algorithms and will be ignored otherwise.
             default: false
        log:
             visibility: user
             type: bool
             description:
              summary: Take the log of the data before reconstruction
                (true or false).
              verbose: Should be set to false if PaganinFilter is
                set beforehand
             default: true
        preview:
             visibility: user
             type: list
             description: A slice list of required frames.
             default: '[]'
        force_zero:
             visibility: param
             type: range
             description: Set any values in the reconstructed image
               outside of this range to zero.
             default: 'None, None'
        ratio:
             visibility: param
             type: float
             description: Ratio of the masks diameter in pixels to
               the smallest edge size along given axis.
             default: 0.95
        log_func:
             visibility: param
             type: int
             description: Override the default log function
             default: np.nan_to_num(-np.log(sino))
        vol_shape:
             visibility: param
             type: str
             description: Override the size of the reconstuction
               volume with an integer value.
             default: fixed

        """