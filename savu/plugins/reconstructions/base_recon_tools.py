from savu.plugins.plugin_tools import PluginTools

class BaseReconTools(PluginTools):
    """A base class for reconstruction plugins
    """
    def define_parameters(self):
        """
        centre_of_rotation:
             visibility: basic
             dtype: [float, str, list[float], dict{int:float}]
             description: Centre of rotation to use for the
               reconstruction.
             default: 0.0
             example: It could be a scalar, a list, or a file
              containing centre of rotations

        outer_pad:
             visibility: basic
             dtype: [bool,int,float]
             description: 'Pad the sinogram width. Choose from True (defaults
                to sqrt(2)), False, or float <= 2.1.'
             warning: This will increase the size of the data and
               the time to compute the reconstruction. Only available
               for selected algorithms and will be ignored otherwise.
             default: 0.1

        ratio:
             visibility: basic
             dtype: float
             description: Ratio of a circular mask diameter in pixels to
               the smallest edge size along given axis.
             default: 0.98

        log:
             visibility: intermediate
             dtype: bool
             description:
                summary: 'Take the log of the data before reconstruction (true or false).'
                verbose: 'Should be set to false if PaganinFilter is set beforehand'
             default: True
             example: Set to True to take the log of the data before reconstruction

        preview:
             visibility: intermediate
             dtype: preview
             description: A slice list of required frames.
             default: '[]'
             example: "[angle, detectorZ, detectorY], where detectorZ is the vertical coordinate,
               detectorY is the horizontal coordinate."

        init_vol:
             visibility: advanced
             dtype: [None,str]
             description: Dataset to use as volume initialiser
               (does not currently work with preview)
             default: None
             example: "Type the name of the initialised dataset
               e.g. ['tomo']"

        centre_pad:
             visibility: advanced
             dtype: [bool,int,float]
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
             example: 'Is it a scalar or a list?'

        force_zero:
             visibility: advanced
             dtype: [list[float,float],list[None,None]]
             description: Set any values in the reconstructed image
               outside of this range to zero.
             default: [None, None]
             example: '[0,1]'

        log_func:
             visibility: advanced
             dtype: str
             description: Override the default log function
             default: np.nan_to_num(-np.log(sino))
             example: You write a function as default

        vol_shape:
             visibility: advanced
             dtype: [str, int]
             description:
               summary: Override the size of the reconstruction
                 volume with an integer value.
               verbose: 'When fixed, you get the dimension of the horizontal
                 detector or you can specify any reconstruction size you like
                 with an integer.'
             default: fixed
        """



