Data Threshold
#################################################################

Description
--------------------------

The module to threshold the data (less, lessequal, equal, greater,
greaterequal) than the given value, based on the condition the data values
will be replaced by the provided new value

    
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
        
        inequality_condition:
            visibility: basic
            dtype: str
            description: Set to less, lessequal, equal, greater, greaterequal
            options: ['less', 'lessequal', 'equal', 'greater', 'greaterequal']
            default: greater
        
        given_value:
            visibility: basic
            dtype: int
            description: The value to be replaced with by inequality_condition.
            default: 1
        
        new_value:
            visibility: basic
            dtype: int
            description: The new value.
            default: 1
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
