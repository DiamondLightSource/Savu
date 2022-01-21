Multi Nxtomo Loader
########################################################

Description
--------------------------

A class to load multiple scans in Nexus format into one dataset. 

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
            dtype: "[str,None]"
            description: The shared part of the name of each file (not including .nxs).
            default: None
        
        dark:
            visibility: basic
            dtype: "[list[filepath, h5path, float], list[None, None, float]]"
            description: Optional path to the dark field data file, nxs path and scale value.
            default: "['None', 'None', 1]"
        
        flat:
            visibility: basic
            dtype: "[list[filepath, h5path, float],list[None,None,float]]"
            description: Optional path to the flat field data file, nxs path and scale value.
            default: "['None', 'None', 1]"
        
        range:
            visibility: basic
            dtype: "list[int,int]"
            description: The start and end of file numbers
            default: "[0, 10]"
        
        angles:
            visibility: basic
            dtype: "[str, int, None]"
            description: If this is 4D data stored in 3D then pass an integer value equivalent to the number of projections per 180 degree scan. If the angles parameter is set to None, then values from default dataset used.
            default: None
        
        name:
            visibility: intermediate
            dtype: str
            description: The name assigned to the dataset.
            default: tomo
        
        data_path:
            visibility: intermediate
            dtype: h5path
            description: Path to the data inside the file.
            default: entry1/tomo_entry/data/data
        
        stack_or_cat:
            visibility: intermediate
            dtype: str
            description: Stack or concatenate the data (4D and 3D respectively)
            default: stack
        
        stack_or_cat_dim:
            visibility: intermediate
            dtype: int
            description: Dimension to stack or concatenate.
            default: "3"
        
        axis_label:
            visibility: intermediate
            dtype: str
            description: "New axis label, if required, in the form 'name.units'"
            default: scan.number
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
