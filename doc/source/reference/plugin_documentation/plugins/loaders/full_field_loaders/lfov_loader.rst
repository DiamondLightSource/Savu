Lfov Loader
########################################################

Description
--------------------------

A class to load 2 scans in Nexus/hdf format into one dataset. 

Parameter definitions
--------------------------

.. code-block:: yaml

        preview:
            visibility: basic
            dtype: preview
            description: A slice list of required frames.
            default: "[]"
        
        file_name:
            visibility: intermediate
            dtype: str
            description: The shared part of the name of each file (not including .nxs)
            default: projection
        
        dark:
            visibility: basic
            dtype: "[list[dir, h5path, float], list[None, None, float]]"
            description: Optional path to the dark field data file, nxs path and scale value.
            default: "['None', 'None', 1]"
        
        flat:
            visibility: basic
            dtype: "[list[dir, h5path, float], list[None, None, float]]"
            description: Optional path to the flat field data file, nxs path and scale value.
            default: "['None', 'None', 1]"
        
        range:
            visibility: hidden
            dtype: "[None,str]"
            description: No need
            default: None
        
        angles:
            visibility: basic
            dtype: "[str, int, None]"
            description: If this is 4D data stored in 3D then pass an integer value equivalent to the number of projections per 180 degree scan. If the angles parameter is set to None, then values from default dataset used.
            default: None
        
        name:
            visibility: hidden
            dtype: str
            description: The name assigned to the dataset.
            default: tomo
        
        data_path:
            visibility: intermediate
            dtype: h5path
            description: Path to the data inside the file.
            default: entry/data/data
        
        stack_or_cat:
            visibility: intermediate
            dtype: str
            description: Stack or concatenate the data (4D and 3D respectively).
            default: stack
        
        stack_or_cat_dim:
            visibility: intermediate
            dtype: int
            description: Dimension to stack or concatenate.
            default: "3"
        
        axis_label:
            visibility: advanced
            dtype: str
            description: "New axis label, if required, in the form 'name.units'."
            default: scan.number
        
        order:
            visibility: basic
            dtype: "list[int]"
            description: Order of datasets used for stitching.
            default: "[1, 0]"
        
        row_offset:
            visibility: basic
            dtype: "list[int]"
            description: Offsets of row indices between datasets.
            default: "[0, -1]"
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
