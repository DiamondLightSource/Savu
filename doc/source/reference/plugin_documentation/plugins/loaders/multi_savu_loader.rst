Multi Savu Loader
########################################################

Description
--------------------------

A class to load multiple savu datasets in Nexus format into one dataset. 

Parameters
--------------------------

.. code-block:: yaml

        preview:
            visibility: basic
            dtype: preview
            description: A slice list of required frames.
            default: "[]"
        
        file_name:
            visibility: basic
            dtype: "[None,str]"
            description: The shared part of the name of each file (not including .nxs).
            default: None
        
        data_path:
            visibility: basic
            dtype: h5path
            description: Path to the data inside the file.
            default: entry1/tomo_entry/data/data
        
        stack_or_cat:
            visibility: intermediate
            dtype: str
            description: Dimension to stack or concatenate.
            default: stack
        
        stack_or_cat_dim:
            visibility: intermediate
            dtype: int
            description: Dimension to stack or concatenate.
            default: "3"
        
        axis_label:
            visibility: intermediate
            dtype: str
            description: "New axis label, if required, in the form 'name.units'."
            default: scan.number
        
        range:
            visibility: basic
            dtype: "list[int,int]"
            description: The start and end of file numbers.
            default: "[0, 10]"
        
        name:
            visibility: intermediate
            dtype: str
            description: Name associated with the data set.
            default: tomo
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
