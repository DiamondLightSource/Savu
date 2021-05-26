Savu Nexus Loader
########################################################

Description
--------------------------

A class to load datasets, and associated metadata, from a Savu output nexus file. By default, the last instance of each unique dataset name will be loaded. Opt instead to load a subset of these datasets, or individual datasets by populating the parameters. 

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
            dtype: "[preview, dict{str:preview}, dict{}]"
            description: A slice list of required frames to apply to ALL datasets, else a dictionary of slice lists where the key is the dataset name.
            default: 
        
        datasets:
            visibility: basic
            dtype: "[list[],list[str]]"
            description: Overuuride the default by choosing specific dataset(s) to load, by stating the NXdata name.
            default: "[]"
        
        names:
            visibility: basic
            dtype: "[list[],list[str]]"
            description: Override the dataset names associated with the datasets parameter above.
            default: "[]"
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
