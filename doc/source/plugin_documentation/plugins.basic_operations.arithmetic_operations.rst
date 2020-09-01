Arithmetic Operations
#################################################################

Description
--------------------------

Basic arithmetic operations on data: addition, subtraction,
multiplication and division. Operations can be performed by extracting
scalars from METADATA (min, max, mean) OR providing a scalar value.

    
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
            description: Create a list of the dataset(s) to create
            default: []
        
        scalar_value:
            visibility: basic
            dtype: int
            description: A scalar value value for arithmetic operation (it not in metadata).
            default: None
        
        operation:
            visibility: intermediate
            dtype: str
            description: Arithmetic operation to apply to data, choose from addition, subtraction, multiplication and division.
            options: ['addition', 'subtraction', 'multiplication', 'division']
            default: division
        
        metadata_value:
            visibility: intermediate
            dtype: str
            description: A type of scalar extracted from metadata (min, max, mean).
            default: max
            options: ['min', 'max', 'mean']
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
