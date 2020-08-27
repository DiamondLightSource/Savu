Basic Operations
#################################################################

Description
--------------------------

A class that performs basic mathematical operations on datasets.How should the information be passed to the plugin?
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        operations:
              visibility: basic
              dtype: list
              description: Operations to perform.
              default: []
        pattern:
              visibility: intermediate
              dtype: str
              description: Pattern associated with the datasets
              default: PROJECTION

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
