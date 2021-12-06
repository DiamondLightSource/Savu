Dezinger Sinogram Gpu
########################################################

Description
--------------------------

A GPU plugin to apply median-based dezinger to SINOGRAM data.     The plugin works in 2D or 3D mode. 

Parameters
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
        
        kernel_size:
            visibility: basic
            dtype: int
            description: Kernel size of the median filter.
            default: "3"
        
        outlier_mu:
            visibility: basic
            dtype: float
            description: A threshold for detecting and removing outliers in data.              If set too small, dezinger acts like a median filter. The value of               the threshold is multiplied with a variance level in data.
            default: "0.1"
        
        kernel_dimension:
            visibility: intermediate
            dtype: str
            description: Select between 2D or 3D kernel for filtering.
            default: 3D
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
