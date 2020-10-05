Strip Background
#################################################################

Description
--------------------------

1D background removal. PyMca magic function

    
Parameter definitions
--------------------------

.. code-block:: yaml

        in_datasets:
            visibility: datasets
            dtype: list
            description: Create a list of the dataset(s) to process
            default: []
        
        out_datasets:
            visibility: datasets
            dtype: list
            description: A list of the dataset(s) to process.
            default: ['in_datasets[0]', 'background']
        
        iterations:
            visibility: intermediate
            dtype: int
            description: Number of iterations.
            default: 100
        
        window:
            visibility: intermediate
            dtype: int
            description: Half width of the rolling window.
            default: 10
        
        SG_filter_iterations:
            visibility: intermediate
            dtype: int
            description: How many iterations until smoothing occurs.
            default: 5
        
        SG_width:
            visibility: intermediate
            dtype: int
            description: Whats the savitzgy golay window.
            default: 35
        
        SG_polyorder:
            visibility: intermediate
            dtype: int
            description: Whats the savitzgy-golay poly order.
            default: 5
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
