Data Removal
#################################################################

Description
--------------------------

A class to remove any unwanted data from the specified pattern frame.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        indices:
            visibility: intermediate
            dtype: list
            description: A list or range of values to remove, e.g. [0, 1, 2]              , 0:2 (start:stop) or 0:2:1 (start:stop:step).
            default: None
        pattern:
            visibility: intermediate
            dtype: int
            description: Explicitly state the slicing pattern.
            default: 'SINOGRAM'
        dim:
            visibility: intermediate
            dtype: int
            description: Data dimension to reduce.
            default: 0

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
