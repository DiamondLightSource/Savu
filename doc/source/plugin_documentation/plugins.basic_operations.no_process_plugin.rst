No Process Plugin
#################################################################

Description
--------------------------

The base class from which all plugins should inherit.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        pattern:
              visibility: intermediate
              dtype: list
              description: Explicitly state the slicing pattern.
              default: None
        dummy:
              visibility: basic
              dtype: int
              description: Dummy parameter for testing.
              default: 10
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
