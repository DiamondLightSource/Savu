Hdf5 Saver
#################################################################

Description
--------------------------

A class to save tomography data to a hdf5 file
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        pattern:
            visibility: basic
            dtype: str
            description: Optimise data storage to this access pattern
              'optimum' will automate this process by choosing the output
              pattern from the previous plugin, if it exists, else the
              first pattern.
            default: 'optimum'
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
