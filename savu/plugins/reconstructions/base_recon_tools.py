from savu.plugins.plugin_tools import PluginTools

class BaseReconTools(PluginTools):
    """
    A base class for reconstruction plugins
    """

    def define_parameters(self):
        """
        centre_of_rotation:
             visibility: basic
             dtype: [float, str, dict{int:float}]
             description: Centre of rotation to use for the reconstruction.
             default: 0.0
             example: It could be a fixed value, a dictionary of 
                 (sinogram number, value) pairs for a polynomial fit of degree
                 1, or a dataset name. 
        init_vol:
             visibility: intermediate
             dtype: [None, str]
             description: Dataset to use as volume initialiser
               (does not currently work with preview)
             default: None
             example: "Type the name of the initialised dataset
               e.g. ['tomo']"
        log:
             visibility: intermediate
             dtype: bool
             description:
                summary: Option to take the log of the data before
                    reconstruction.
                verbose: Should be set to false if you use PaganinFilter
             default: True
             example: Set to True to take the log of the data before
                 reconstruction.
        preview:
             visibility: intermediate
             dtype: preview
             description: A slice list of required frames.
             default: []
        force_zero:
             visibility: intermediate
             dtype: [list[float,float],list[None,None]]
             description: Set any values in the reconstructed image
               outside of this range to zero.
             default: [None, None]
             example: [0,1]
        ratio:
             visibility: intermediate
             dtype: [float, list[float, float]]
             description: Ratio of the masks diameter in pixels to
               the smallest edge size along given axis. If a list of two floats
               is given, the second value is used to fill up the area outside
               the mask.
             default: 0.95
        log_func:
             visibility: advanced
             dtype: str
             description: Override the default log function with a numpy
                 statement
             default: np.nan_to_num(-np.log(sino))
        vol_shape:
             visibility: intermediate
             dtype: [str, int]
             description:
               summary: Override the size of the reconstruction
                 volume with an integer value.
               verbose: When fixed, you get the dimension of the horizontal
                 detector or you can specify any reconstruction size you like
                 with an integer.
             default: fixed           
        """


