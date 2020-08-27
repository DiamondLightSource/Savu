Nxxrd Loader
#################################################################

Description
--------------------------

A class to load tomography data from an NXxrd file.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        name:
            visibility: basic
            dtype: str
            description: The name assigned to the dataset.
            default: xrd
        calibration_path:
            visibility: basic
            dtype: str
            description: Path to the calibration file
            default: None
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
