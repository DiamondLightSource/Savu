Mrc Loader
#################################################################

Description
--------------------------

Load Medical Research Council (MRC) formatted image data.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        angles:
            visibility: basic
            dtype: str
            description: A python statement to be evaluated              (e.g np.linspace(0, 180, nAngles)) or a file.
            default: None
        name:
            visibility: basic
            dtype: str
            description: The name assigned to the dataset
            default: tomo
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
