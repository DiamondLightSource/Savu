Base I18 Multi Modal Loader
#################################################################

Description
--------------------------

This class provides a base for all multi-modal loaders
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        fast_axis:
            visibility: basic
            dtype: str
            description: What is the fast axis called.
            default: 'x'
        scan_pattern:
            visibility: intermediate
            dtype: list
            description: What was the scan.
            default: ["rotation","x"]
        x:
            visibility: intermediate
            dtype: int_path
            description: Where is x in the file.
            default: 'entry1/raster_counterTimer01/traj1ContiniousX'
        y:
            visibility: intermediate
            dtype: int_path
            description: Where is y in the file
            default: None
        rotation:
            visibility: intermediate
            dtype: int_path
            description: Where is rotation in the file
            default: 'entry1/raster_counterTimer01/sc_sample_thetafine'
        monochromator:
            visibility: intermediate
            dtype: int_path
            description: Where is the monochromator
            default: 'entry1/instrument/DCM/energy'

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
