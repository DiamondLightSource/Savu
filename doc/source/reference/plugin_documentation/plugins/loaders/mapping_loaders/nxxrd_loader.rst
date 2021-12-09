Nxxrd Loader
########################################################

Description
--------------------------

A class to load tomography data from an NXxrd file. 

Parameters
--------------------------

.. code-block:: yaml

        preview:
            visibility: basic
            dtype: preview
            description: A slice list of required frames.
            default: "[]"
        
        name:
            visibility: basic
            dtype: str
            description: The name assigned to the dataset.
            default: xrd
        
        calibration_path:
            visibility: basic
            dtype: "[None,str]"
            description: Path to the calibration file
            default: None
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
