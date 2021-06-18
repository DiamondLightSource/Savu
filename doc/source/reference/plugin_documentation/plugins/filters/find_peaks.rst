Find Peaks
########################################################

Description
--------------------------

This plugin uses peakutils to find peaks in spectra. This is then metadata. 

Parameter definitions
--------------------------

.. code-block:: yaml

        in_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: 
                summary: A list of the dataset(s) to process.
                verbose: A list of strings, where each string gives the name of a dataset that was either specified by a loader plugin or created as output to a previous plugin.  The length of the list is the number of input datasets requested by the plugin.  If there is only one dataset and the list is left empty it will default to that dataset.
            default: "[]"
        
        out_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: Create a list of the dataset(s).
            default: "['Peaks']"
        
        thresh:
            visibility: basic
            dtype: float
            description: Threshold for peak detection
            default: "0.03"
        
        min_distance:
            visibility: basic
            dtype: int
            description: Minimum distance for peak detection.
            default: "15"
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
