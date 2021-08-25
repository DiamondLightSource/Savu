Inpainting
########################################################

Description
--------------------------

A plugin to apply 2D/3D inpainting technique to data. If there is a chunk of data missing or one needs to inpaint some data features. 

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
        
        mask_range:
            visibility: basic
            dtype: "list[float,float]"
            description: mask for inpainting is set as a threshold in a range.
            default: "[1.0, 100]"
        
        iterations:
            visibility: basic
            dtype: float
            description: controls the smoothing level of the inpainted region.
            default: "50"
        
        windowsize_half:
            visibility: basic
            dtype: int
            description: half-size of the smoothing window.
            default: "3"
        
        sigma:
            visibility: basic
            dtype: float
            description: maximum value for the inpainted region.
            default: "0.5"
        
        pattern:
            visibility: basic
            dtype: str
            description: Pattern to apply these to.
            default: SINOGRAM
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
