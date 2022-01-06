{% extends "/home/glb23482/git_projects/Savu/doc/source/reference/savu_commands/plugin_template.rst" %}

{% block title %}Tomo Phantom Artifacts{% endblock %}

{% block description %}
A plugin to add artifacts to real or generated synthetic data using TomoPhantom 
{% endblock %}

{% block parameter_yaml %}

        in_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: Default input dataset names.
            default: "['synth_proj_data']"
        
        out_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: Default out dataset names.
            default: "['synth_proj_data_artifacts']"
        
        pattern:
            visibility: advanced
            dtype: str
            description: Pattern to apply this to.
            default: SINOGRAM
        
        artifacts_noise_type:
            visibility: intermediate
            dtype: str
            description: Set the noise type, Poisson or Gaussian.
            default: Poisson
        
        artifacts_noise_amplitude:
            visibility: intermediate
            dtype: float
            description: Define the amplitude of noise.
            default: "100000"
            dependency: artifacts_noise_type
        
        datashifts_maxamplitude_pixel:
            visibility: advanced
            dtype: "[None,int]"
            description: Incorporate misalignment into projections (in pixels), requires PROJECTION pattern.
            default: None
        
        datashifts_maxamplitude_subpixel:
            visibility: advanced
            dtype: "[None,float]"
            description: Incorporate misalignment into projections (in subpixel resolution), requires PROJECTION pattern.
            default: None
        
        artifacts_zingers_percentage:
            visibility: intermediate
            dtype: "[None,float]"
            description: Add broken pixels to projections, a percent from total pixels number
            default: None
        
        artifacts_zingers_modulus:
            visibility: advanced
            dtype: int
            description: modulus to control the amount of 4/6 pixel clusters (zingers) to be added
            default: "10"
            dependency: artifacts_zingers_percentage
        
        artifacts_stripes_percentage:
            visibility: intermediate
            dtype: "[None,float]"
            description: The amount of stripes in the data (percent-wise), applied to SINOGRAM data.
            default: None
        
        artifacts_stripes_maxthickness:
            visibility: advanced
            dtype: float
            description: Defines the maximal thickness of a stripe.
            default: "3.0"
            dependency: artifacts_stripes_percentage
        
        artifacts_stripes_intensity:
            visibility: advanced
            dtype: float
            description: To incorporate the change of intensity in the stripe.
            default: "0.3"
            dependency: artifacts_stripes_percentage
        
        artifacts_stripes_type:
            visibility: advanced
            dtype: str
            options: "['full', 'partial']"
            description: Set the stripe type to full or partial.
            default: full
            dependency: artifacts_stripes_percentage
        
        artifacts_stripes_variability:
            visibility: advanced
            dtype: float
            description: The intensity variability of a stripe.
            default: "0.007"
            dependency: artifacts_stripes_percentage
        
        artifacts_pve:
            visibility: advanced
            dtype: "[None,int]"
            description: the strength of partial volume effect, linked to the               limited resolution of the detector, try 1 or 3
            default: None
        
        artifacts_fresnel_distance:
            visibility: advanced
            dtype: "[None,int]"
            description: observation distance for fresnel propagator, e.g. 20
            default: None
        
        artifacts_fresnel_scale_factor:
            visibility: advanced
            dtype: float
            description: fresnel propagator sacaling
            default: "10"
            dependency: artifacts_fresnel_distance
        
        artifacts_fresnel_wavelenght:
            visibility: advanced
            dtype: float
            description: fresnel propagator wavelength
            default: "0.003"
            dependency: artifacts_fresnel_distance
        
{% endblock %}

{% block plugin_citations %}
        
        **TomoPhantom, a software package to generate 2D-4D analytical phantoms for CT image reconstruction algorithm benchmarks by Kazantsev, Daniil et al.**
        
        **Bibtex**
        
        .. code-block:: none
        
            @article{kazantsev2018tomophantom,
              title={TomoPhantom, a software package to generate 2D-4D analytical phantoms for CT image reconstruction algorithm benchmarks},
              author={Kazantsev, Daniil and Pickalov, Valery and Nagella, Srikanth and Pasca, Edoardo and Withers, Philip J},
              journal={SoftwareX},
              volume={7},
              pages={150--155},
              year={2018},
              publisher={Elsevier}
            }
            
        
        **Endnote**
        
        .. code-block:: none
        
            %0 Journal Article
            %T TomoPhantom, a software package to generate 2D-4D analytical phantoms for CT image reconstruction algorithm benchmarks
            %A Kazantsev, Daniil
            %A Pickalov, Valery
            %A Nagella, Srikanth
            %A Pasca, Edoardo
            %A Withers, Philip J
            %J SoftwareX
            %V 7
            %P 150-155
            %@ 2352-7110
            %D 2018
            %I Elsevier
            
        
        
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.simulation.tomo_phantom_artifacts.rst{% endblock %}
