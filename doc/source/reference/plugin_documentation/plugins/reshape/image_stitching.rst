Image Stitching
########################################################

Description
--------------------------

Method to stitch images of two tomo-datasets including flat-field correction. 

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
        
        overlap:
            visibility: basic
            dtype: int
            description: Overlap width between two images.
            default: "354"
        
        row_offset:
            visibility: basic
            dtype: int
            description: Offset of row indices of projections in the second dataset compared to the first dataset.
            default: "-1"
        
        crop:
            visibility: basic
            dtype: "list[int,int,int,int]"
            description: "Parameters used to crop stitched image with respect to the edges of an image. Format: [crop_top, crop_bottom, crop_left, crop_right]."
            default: "[0, 0, 250, 250]"
        
        pattern:
            visibility: intermediate
            dtype: str
            description: "Data processing pattern is 'PROJECTION' or 'SINOGRAM'."
            default: PROJECTION
            options: "['PROJECTION', 'SINOGRAM']"
        
        norm:
            visibility: intermediate
            dtype: bool
            description: Apply normalization before stitching.
            default: "True"
        
        flat_use:
            visibility: intermediate
            dtype: bool
            description: Apply flat-field correction.
            default: "True"
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
