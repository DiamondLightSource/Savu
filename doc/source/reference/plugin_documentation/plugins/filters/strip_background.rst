Strip Background
########################################################

Description
--------------------------

1D background removal. PyMca magic function 

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
            description: A list of the dataset(s) to process.
            default: "['in_datasets[0]', 'background']"
        
        iterations:
            visibility: basic
            dtype: int
            description: Number of iterations.
            default: "100"
        
        window:
            visibility: basic
            dtype: int
            description: Half width of the rolling window.
            default: "10"
        
        SG_filter_iterations:
            visibility: intermediate
            dtype: int
            description: How many iterations until smoothing occurs.
            default: "5"
        
        SG_width:
            visibility: intermediate
            dtype: int
            description: Whats the savitzgy golay window.
            default: "35"
        
        SG_polyorder:
            visibility: intermediate
            dtype: int
            description: Whats the savitzgy-golay poly order.
            default: "5"
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
