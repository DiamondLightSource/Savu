Ring Removal Normalization
########################################################

Description
--------------------------

Method to remove stripe artefacts in a sinogram (<-> ring artefacts in a reconstructed image) using a normalization-based method. A simple improvement to handle partial stripes is included. 

.. toctree::
    Plugin documention and guidelines on use </../../../plugin_guides/plugins/ring_removal/ring_removal_normalization_doc.rst>

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
        
        radius:
            visibility: intermediate
            dtype: int
            description: Radius of the Gaussian kernel.
            default: "11"
        
        number_of_chunks:
            visibility: intermediate
            dtype: int
            description: Divide the sinogram to many chunks of rows
            default: "1"
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
