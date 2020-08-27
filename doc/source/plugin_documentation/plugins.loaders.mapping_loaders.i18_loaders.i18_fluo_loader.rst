I18 Fluo Loader
#################################################################

Description
--------------------------

A class to load I18's data from an NXstxm file
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        fluo_detector:
            visibility: basic
            dtype: str
            description: Path to fluo.
            default: 'entry1/xspress3/AllElementSum'
        name:
            visibility: basic
            dtype: str
            description: The new name assigned to the dataset.
            default: 'fluo'

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
