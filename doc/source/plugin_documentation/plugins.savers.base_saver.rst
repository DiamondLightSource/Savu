Base Saver
#################################################################

Description
--------------------------

A base plugin from which all data saver plugins should inherit.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        out_datasets:
            visibility: datasets
            dtype: list
            description: none
            default: []
        in_datasets:
            visibility: datasets
            dtype: list
            description: none
            default: []
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
