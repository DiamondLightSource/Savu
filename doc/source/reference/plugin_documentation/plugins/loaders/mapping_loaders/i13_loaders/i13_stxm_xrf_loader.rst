I13 Stxm Xrf Loader
########################################################

Description
--------------------------

A class for loading nxstxm data

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
            dtype: preview
            description: A slice list of required frames.
            default: "[]"
        
        is_map:
            visibility: basic
            dtype: bool
            description: Is it a map.
            default: "True"
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
