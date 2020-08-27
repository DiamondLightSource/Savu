I18 Stxm Loader
#################################################################

Description
--------------------------

A class to load I18's data from a Nxstxm file
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        monitor_detector:
            visibility: basic
            dtype: str
            description: Path to stxm.
            default: 'entry1/raster_counterTimer01/It'
        name:
            visibility: basic
            dtype: str
            description: The new name assigned to the dataset.
            default: 'stxm'

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
