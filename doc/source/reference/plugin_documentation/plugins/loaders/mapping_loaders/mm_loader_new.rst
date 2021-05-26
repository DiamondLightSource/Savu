Mm Loader New
########################################################

Description
--------------------------

Testing the new mmloader plugin 

Parameter definitions
--------------------------

.. code-block:: yaml

        in_datasets:
            visibility: not
            dtype: "[list[],list[str]]"
            description: Create a list of the dataset(s) to process
            default: "[]"
        
        out_datasets:
            visibility: not
            dtype: "[list[],list[str]]"
            description: Create a list of the dataset(s) to create
            default: "[]"
        
        preview:
            visibility: basic
            dtype: "[list, dict]"
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
