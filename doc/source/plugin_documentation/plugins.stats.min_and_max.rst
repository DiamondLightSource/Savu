Min And Max
#################################################################

Description
--------------------------

A plugin to calculate the min and max values of each slice (as determined
by the pattern parameter)
    
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
            dtype: str
            description: The default names.
            default: ['the_min', 'the_max']
        
        pattern:
            visibility: intermediate
            dtype: tuple
            description: How to slice the data.
            default: VOLUME_XZ
        
        smoothing:
            visibility: intermediate
            dtype: bool
            description: Apply a smoothing filter or not.
            default: True
        
        masking:
            visibility: intermediate
            dtype: bool
            description: Apply a circular mask or not.
            default: True
        
        ratio:
            visibility: intermediate
            dtype: float
            description: Used to calculate the circular mask. If not provided, it is calculated using the center of rotation.
            default: None
        
        method:
            visibility: intermediate
            dtype: str
            options: ['extrema', 'percentile']
            description: Method to find the global min and the global max.
            default: percentile
        
        p_range:
            visibility: intermediate
            dtype: range
            description: "Percentage range if use the 'percentile' method."
            default: [0.0, 100.0]
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
