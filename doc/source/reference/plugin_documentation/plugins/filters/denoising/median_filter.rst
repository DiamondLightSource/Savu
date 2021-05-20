Median Filter
########################################################

Description
--------------------------

A plugin to apply 2D/3D median filter. The 3D capability is enabled through padding. Note that the kernel_size in 2D will be kernel_size x kernel_size and in 3D case kernel_size x kernel_size x kernel_size. 

.. toctree::
    Plugin documention and guidelines on use </../../../plugin_guides/plugins/filters/denoising/median_filter_doc.rst>

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
        
        kernel_size:
            visibility: basic
            dtype: int
            description: Kernel size of the median filter.
            default: "3"
        
        dimension:
            visibility: advanced
            dtype: str
            description: Dimensionality of the filter 2D/3D.
            default: 3D
        
        pattern:
            visibility: advanced
            dtype: str
            description: Pattern to apply this to.
            default: PROJECTION
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
