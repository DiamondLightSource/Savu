from savu.plugins.plugin_tools import PluginTools

class PtypyCompactTools(PluginTools):
    """This plugin performs ptychography using the ptypy package.
    """
    def define_parameters(self):
        """
        data_center:
              visibility: intermediate
              dtype: [list[float], str, None]
              description: 'Center (pixel) of the optical axes in raw data'
              default: None
        data_orientation:
              visibility: intermediate
              dtype: [list,None]
              description: See online documentation
              default: None
        data_auto_center:
              visibility: intermediate
              dtype: bool
              description: See online documentation
              default: True
        geometry_shape:
              visibility: intermediate
              dtype: int
              description: See online documentation
              default: 128
        illumination_photons:
              visibility: intermediate
              dtype: [None,list]
              description: See online documentation
              default: None
        illumination_diversity_noise:
              visibility: intermediate
              dtype: [None,float]
              description: See online documentation
              default: None
        illumination_diversity_power:
              visibility: intermediate
              dtype: int
              description: See online documentation
              default: 0.1
        illumination_diversity_shift:
              visibility: intermediate
              dtype: [None,float]
              description: See online documentation
              default: None
        sample_model:
              visibility: intermediate
              dtype: [None,str]
              description: See online documentation
              default: None
        sample_fill:
              visibility: intermediate
              dtype: int
              description: See online documentation
              default: 1
        sample_diversity_noise:
              visibility: intermediate
              dtype: [None,float]
              description: See online documentation
              default: None
        sample_diversity_power:
              visibility: intermediate
              dtype: float
              description: See online documentation
              default: 0.1
        sample_diversity_shift:
              visibility: intermediate
              dtype: [None,float]
              description: See online documentation
              default: None
        coherence_num_probe_modes:
              visibility: intermediate
              dtype: int
              description: See online documentation
              default: 1
        coherence_num_object_modes:
              visibility: intermediate
              dtype: int
              description: See online documentation
              default: 1
        coherence_spectrum:
              visibility: intermediate
              dtype: [None,list]
              description: See online documentation
              default: None
        coherence_object_dispersion:
              visibility: intermediate
              dtype: [None,float]
              description: See online documentation
              default: None
        coherence_probe_dispersion:
              visibility: intermediate
              dtype: [None,float]
              description: See online documentation
              default: None
        common_numiter_contiguous:
              visibility: intermediate
              dtype: int
              description: See online documentation
              default: 1
        common_probe_support:
              visibility: intermediate
              dtype: float
              description: See online documentation
              default: 0.7
        common_clip_object:
              visibility: intermediate
              dtype: [None,list]
              description: See online documentation
              default: None
        DM_num_iter:
              visibility: intermediate
              dtype: int
              description: See online documentation
              default: 30
        DM_alpha:
              visibility: intermediate
              dtype: int
              description: See online documentation
              default: 1
        DM_probe_update_start:
              visibility: intermediate
              dtype: int
              description: See online documentation
              default: 2
        DM_update_object_first:
              visibility: intermediate
              dtype: bool
              description: See online documentation
              default: True
        DM_overlap_converge_factor:
              visibility: intermediate
              dtype: float
              description: See online documentation
              default: 0.05
        DM_overlap_max_iterations:
              visibility: intermediate
              dtype: int
              description: See online documentation
              default: 10
        DM_probe_inertia:
              visibility: intermediate
              dtype: float
              description: See online documentation
              default: 0.001
        DM_object_inertia:
              visibility: intermediate
              dtype: float
              description: See online documentation
              default: 0.1
        DM_fourier_relax_factor:
              visibility: intermediate
              dtype: float
              description: See online documentation
              default: 0.01
        DM_obj_smooth_std:
              visibility: intermediate
              dtype: int
              description: See online documentation
              default: 20
        ML_num_iter:
              visibility: intermediate
              dtype: int
              description: See online documentation
              default: 5
        ML_type:
              visibility: intermediate
              dtype: str
              description: See online documentation
              default: 'gaussian'
        ML_floating_intensities:
              visibility: intermediate
              dtype: bool
              description: See online documentation
              default: False
        ML_intensity_renormalization:
              visibility: intermediate
              dtype: int
              description: See online documentation
              default: 1
        ML_reg_del2:
              visibility: intermediate
              dtype: bool
              description: See online documentation
              default: True
        ML_reg_del2_amplitude:
              visibility: intermediate
              dtype: float
              description: See online documentation
              default: 0.01
        ML_smooth_gradient:
              visibility: intermediate
              dtype: int
              description: See online documentation
              default: 0
        ML_scale_precond:
              visibility: intermediate
              dtype: bool
              description: See online documentation
              default: False
        ML_scale_probe_object:
              visibility: intermediate
              dtype: int
              description: See online documentation
              default: 1
        ML_probe_update_start:
              visibility: intermediate
              dtype: int
              description: See online documentation
              default: 0

        """