I18 Xrd Loader
#################################################################

Description
--------------------------

A class to load I18's data from an xrd file
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        monitor_detector:
            visibility: basic
            dtype: str
            description: Path to the folder containing the data.
            default: None
        calibration_path:
            visibility: basic
            dtype: int_path
            description: path to the calibration file.
            default: None
        name:
            visibility: basic
            dtype: str
            description: The new name assigned to the dataset.
            default: 'xrd'

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
