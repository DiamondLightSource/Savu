Mm Loader
########################################################

Description
--------------------------

Testing the mmloader plugin 

Parameters
--------------------------

.. code-block:: yaml

        preview:
            visibility: basic
            dtype: "[preview, dict{str: preview},dict{}]"
            description: A slice list of required frames to apply to ALL datasets, else a dictionary of slice lists where the key is the dataset name.
            default: "[]"
        
        dataset_names:
            visibility: basic
            dtype: "list[str, str, str, str]"
            description: "The names assigned to each dataset in the order [fluorescence, diffraction, absorption, monitor]"
            default: "['fluo', 'xrd', 'stxm', 'monitor']"
        
        fluo_offset:
            visibility: basic
            dtype: float
            description: fluo scale offset.
            default: "0.0"
        
        fluo_gain:
            visibility: intermediate
            dtype: float
            description: fluo gain
            default: "0.01"
        
        calibration_path:
            visibility: basic
            dtype: "[None,str]"
            description: Path to the calibration file
            default: None
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
