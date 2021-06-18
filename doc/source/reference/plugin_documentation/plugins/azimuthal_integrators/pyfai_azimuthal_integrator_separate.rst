Pyfai Azimuthal Integrator Separate
########################################################

Description
--------------------------

1D azimuthal integrator by pyFAI 

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
            description: Names assigned to datasets created as output to the plugin.
            default: "['powder', 'spots']"
        
        use_mask:
            visibility: basic
            dtype: bool
            description: Option to apply a mask.
            default: "False"
        
        num_bins:
            visibility: basic
            dtype: int
            description: Number of bins.
            default: "1005"
        
        percentile:
            visibility: intermediate
            dtype: int
            description: Percentile to threshold
            default: "50"
        
        num_bins_azim:
            visibility: basic
            dtype: int
            description: Number of azimuthal bins.
            default: "20"
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
