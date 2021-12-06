Nxfluo Loader
########################################################

Description
--------------------------

A class to load tomography data from an NXFluo file. 

Parameters
--------------------------

.. code-block:: yaml

        preview:
            visibility: basic
            dtype: preview
            description: A slice list of required frames.
            default: "[]"
        
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
        
        name:
            visibility: basic
            dtype: str
            description: The name assigned to the dataset.
            default: fluo
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
