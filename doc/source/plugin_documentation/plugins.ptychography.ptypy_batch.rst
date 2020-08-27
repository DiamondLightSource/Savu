Ptypy Batch
#################################################################

Description
--------------------------

This plugin performs ptychography using the ptypy package.
The same parameter set is used across all slices and is based
on the output from a previous reconstruction.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        ptyr_file:
              visibility: basic
              dtype: str
              description: The ptyd for a previously successful reconstruction.
              default: '/dls/science/users/clb02321/DAWN_stable/I13Test_Catalysts/processing/catalyst_data/analysis92713/recons/92713/92713_DM_0030_0.ptyr'
        mask_file:
              visibility: basic
              dtype: list
              description: The mask file.
              default: "['probe', 'object_transmission', 'positions']"
        mask_entry:
              visibility: basic
              dtype: str
              description: The mask entry.
              default: '/mask'

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
