from savu.plugins.plugin_tools import PluginTools

class PtypyBatchTools(PluginTools):
    """This plugin performs ptychography using the ptypy package.
    The same parameter set is used across all slices and is based
    on the output from a previous reconstruction.
    """
    def define_parameters(self):
        """
        ptyr_file:
              visibility: basic
              dtype: str
              description: The ptyd for a previously successful reconstruction.
              default: '/dls/science/users/clb02321/DAWN_stable/I13Test_Catalysts/processing/catalyst_data/analysis92713/recons/92713/92713_DM_0030_0.ptyr'
        mask_file:
              visibility: basic
              dtype: str
              description: The mask file.
              default: '/dls/science/users/clb02321/DAWN_stable/I13Test_Catalysts/processing/catalyst_data/analysis92713/new_mask2.hdf'
        mask_entry:
              visibility: basic
              dtype: str
              description: The mask entry.
              default: '/mask'

        """