Forward Projector Cpu
########################################################

Description
--------------------------

This plugin uses ToMoBAR software and CPU Astra projector to generate parallel-beam projection data. The plugin will project the given object using the available metadata OR user-provided geometry. In case when angles set to None, the metadata projection geometry will be used. 

Parameters
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
            description: The default names
            default: "['forw_proj']"
        
        angles_deg:
            visibility: advanced
            dtype: "[None, list[float,float,int]]"
            description: "Projection angles in degrees in a format [start, stop, total number of angles]."
            default: None
        
        det_horiz:
            visibility: advanced
            dtype: "[None,int]"
            description: The size of the horizontal detector.
            default: None
        
        centre_of_rotation:
            visibility: advanced
            dtype: "[None,float]"
            description: The centre of rotation.
            default: None
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
