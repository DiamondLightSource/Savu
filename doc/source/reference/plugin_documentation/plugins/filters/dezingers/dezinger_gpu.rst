Dezinger Gpu
########################################################

Description
--------------------------

A plugin to apply 2D/3D median-based dezinger on GPU. The 3D capability is enabled    through padding. Note that the kernel_size in 2D will be kernel_size x kernel_size and in 3D case kernel_size x kernel_size x kernel_size. 

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
        
        outlier_mu:
            visibility: basic
            dtype: float
            description: Threshold for defecting outliers, greater is less sensitive. If very small, dezinger acts like a median filter.
            default: "1.0"
        
        kernel_size:
            visibility: basic
            dtype: int
            description: Kernel size of the median filter.
            default: "3"
        
        dimension:
            visibility: intermediate
            dtype: str
            description: dimensionality of the filter 2D/3D.
            default: 3D
        
        pattern:
            visibility: basic
            dtype: str
            description: Pattern to apply this to.
            default: PROJECTION
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
