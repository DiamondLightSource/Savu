I18 Monitor Loader
#################################################################

Description
--------------------------

A class to load I18's data from a monitor file
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        monitor_detector:
            visibility: basic
            dtype: str
            description: Path to monitor.
            default: 'entry1/raster_counterTimer01/I0'
        name:
            visibility: basic
            dtype: str
            description: The new name assigned to the dataset.
            default: 'monitor'

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
