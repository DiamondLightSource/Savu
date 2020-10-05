Elementwise Arrays Arithmetics
#################################################################

Description
--------------------------

Basic arithmetic operations on two input datasets:
addition, subtraction, multiplication and division.

    
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
        
        operation:
            visibility: basic
            dtype: str
            description: Arithmetic operation to apply to data, choose from addition, subtraction, multiplication and division.
            options: ['addition', 'subtraction', 'multiplication', 'division']
            default: multiplication
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
