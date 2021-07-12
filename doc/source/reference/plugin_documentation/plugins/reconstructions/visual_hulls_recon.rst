Visual Hulls Recon
########################################################

Description
--------------------------

A Plugin to reconstruct an image by filter back projection using the inverse radon transform from scikit-image. 

Parameter definitions
--------------------------

.. code-block:: yaml

        in_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: 
                summary: A list of the dataset(s) to process.
                verbose: A list of strings, where each string gives the name of a dataset that was either specified by a loader plugin or created as output to a previous plugin.  The length of the list is the number of input datasets requested by the plugin.  If there is only one dataset and the list is left empty it will default to that dataset.
            default: "[]"
        
        out_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: 
                summary: A list of the dataset(s) to create.
                verbose: A list of strings, where each string is a name to be assigned to a dataset output by the plugin. If there is only one input dataset and one output dataset and the list is left empty, the output will take the name of the input dataset. The length of the list is the number of output datasets created by the plugin.
            default: "[]"
        
        centre_of_rotation:
            visibility: basic
            dtype: "[float, str, dict{int:float}]"
            description: Centre of rotation to use for the reconstruction.
            default: "0.0"
            example: It could be a fixed value, a dictionary of (sinogram number, value) pairs for a polynomial fit of degree 1, or a dataset name.
        
        init_vol:
            visibility: hidden
            dtype: "[None, str]"
            description: Dataset to use as volume initialiser (does not currently work with preview)
            default: None
            example: "Type the name of the initialised dataset e.g. ['tomo']"
        
        log:
            visibility: intermediate
            dtype: bool
            description: 
                summary: Option to take the log of the data before reconstruction.
                verbose: Should be set to false if you use PaganinFilter
            default: "True"
            example: Set to True to take the log of the data before reconstruction.
        
        preview:
            visibility: intermediate
            dtype: preview
            description: A slice list of required frames.
            default: "[]"
        
        force_zero:
            visibility: intermediate
            dtype: "[list[float,float],list[None,None]]"
            description: Set any values in the reconstructed image outside of this range to zero.
            default: "['None', 'None']"
            example: "[0, 1]"
        
        ratio:
            visibility: intermediate
            dtype: "[float, list[float, float]]"
            description: Ratio of the masks diameter in pixels to the smallest edge size along given axis. If a list of two floats is given, the second value is used to fill up the area outside the mask.
            default: "0.95"
        
        log_func:
            visibility: advanced
            dtype: str
            description: Override the default log function with a numpy statement
            default: np.nan_to_num(-np.log(sino))
        
        vol_shape:
            visibility: intermediate
            dtype: "[str, int]"
            description: 
                summary: Override the size of the reconstruction volume with an integer value.
                verbose: When fixed, you get the dimension of the horizontal detector or you can specify any reconstruction size you like with an integer.
            default: fixed
        
        threshold:
            visibility: basic
            dtype: float
            description: Threshold to binarize the input sinogram.
            default: "0.5"
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml

Citations
--------------------------

The visual hull concept for silhouette-based image understanding by Laurentini, Aldo et al.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Bibtex
""""""""""""""""""""""""""""""""""""""""""

.. code-block:: none

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
    

Endnote
""""""""""""""""""""""""""""""""""""""""""

.. code-block:: none

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
    

