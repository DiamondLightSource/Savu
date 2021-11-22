Mc Near Absorption Correction
########################################################

Description
--------------------------

McNears absorption correction, takes in a normalised absorption sinogram and xrf sinogram stack. 

Parameters
--------------------------

.. code-block:: yaml

        in_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: A list of the dataset(s) to process.
            default: "['xrf', 'stxm']"
        
        out_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: 
                summary: A list of the dataset(s) to create.
                verbose: A list of strings, where each string is a name to be assigned to a dataset output by the plugin. If there is only one input dataset and one output dataset and the list is left empty, the output will take the name of the input dataset. The length of the list is the number of output datasets created by the plugin.
            default: "[]"
        
        azimuthal_offset:
            visibility: basic
            dtype: float
            description: Angle between detectors.
            default: "-90.0"
        
        density:
            visibility: intermediate
            dtype: float
            description: The density
            default: "3.5377"
        
        compound:
            visibility: intermediate
            dtype: str
            description: The compound
            default: Co0.1Re0.01Ti0.05(SiO2)0.84
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
