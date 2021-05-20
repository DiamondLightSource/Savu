I18 Xrd Loader
#################################################################

Description
--------------------------

A class to load I18's data from an xrd file
    
Parameter definitions
--------------------------

.. code-block:: yaml

        in_datasets:
            visibility: not
            dtype: list
            description: Create a list of the dataset(s) to process
            default: []
        
        out_datasets:
            visibility: not
            dtype: list
            description: Create a list of the dataset(s) to create
            default: []
        
        preview:
            visibility: basic
            dtype: preview
            description: A slice list of required frames.
            default: []
        
        data_file:
            visibility: hidden
            dtype: str
            description: hidden parameter for savu template
            default: <>
        
        fast_axis:
            visibility: basic
            dtype: str
            description: What is the fast axis called.
            default: x
        
        scan_pattern:
            visibility: intermediate
            dtype: list
            description: What was the scan.
            default: ['rotation', 'x']
        
        x:
            visibility: intermediate
            dtype: int_path
            description: Where is x in the file.
            default: entry1/raster_counterTimer01/traj1ContiniousX
        
        y:
            visibility: intermediate
            dtype: int_path
            description: Where is y in the file
            default: None
        
        rotation:
            visibility: intermediate
            dtype: int_path
            description: Where is rotation in the file
            default: entry1/raster_counterTimer01/sc_sample_thetafine
        
        monochromator:
            visibility: intermediate
            dtype: int_path
            description: Where is the monochromator
            default: entry1/instrument/DCM/energy
        
        monitor_detector:
            visibility: basic
            dtype: str
            description: Path to the folder containing the data.
            default: None
        
        calibration_path:
            visibility: basic
            dtype: int_path
            description: path to the calibration file.
            default: None
        
        name:
            visibility: basic
            dtype: str
            description: The new name assigned to the dataset.
            default: xrd
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
