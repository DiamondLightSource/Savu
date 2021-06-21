I13 Speckle Loader
########################################################

Description
--------------------------

A class to load tomography data from an NXstxm file 

Parameter definitions
--------------------------

.. code-block:: yaml

        preview:
            visibility: basic
            dtype: preview
            description: A slice list of required frames.
            default: "[]"
        
        signal_key:
            visibility: basic
            dtype: h5path
            description: Path to the signals
            default: /entry/sample
        
        reference_key:
            visibility: intermediate
            dtype: h5path
            description: Path to the reference
            default: /entry/reference
        
        angle_key:
            visibility: intermediate
            dtype: h5path
            description: Path to the reference
            default: /entry/theta
        
        dataset_names:
            visibility: intermediate
            dtype: list
            description: The output sets.
            default: "['signal', 'reference']"
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
