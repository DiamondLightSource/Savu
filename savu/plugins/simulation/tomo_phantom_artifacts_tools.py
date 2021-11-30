from savu.plugins.plugin_tools import PluginTools


class TomoPhantomArtifactsTools(PluginTools):
    """A plugin to add artifacts to the generated synthetic data using TomoPhantom
    """

    def define_parameters(self):        
        """
        pattern:
             visibility: advanced
             dtype: str
             description: Pattern to apply this to.
             default: 'SINOGRAM'
        artifacts_noise_type:
              visibility: intermediate
              dtype: str
              description: Set the noise type, Poisson or Gaussian.
              default: Poisson
        artifacts_noise_amplitude:
              visibility: intermediate
              dtype: float
              description: Define the amplitude of noise.
              default: 100000
              dependency:
                artifacts_noise_type
        artifacts_misalignment_maxamplitude:
              visibility: advanced
              dtype: [None,int]
              description: Incorporate misalignment into projections (in pixels).
              default: None
        artifacts_zingers_percentage:
              visibility: intermediate
              dtype: [None,float]
              description: Add broken pixels to projections, a percent from total pixels number
              default: None
        artifacts_zingers_modulus:
              visibility: advanced
              dtype: int
              description: modulus to control the amount of 4/6 pixel clusters (zingers) to be added
              default: 10
              dependency:
                artifacts_zingers_percentage
        artifacts_stripes_percentage:
              visibility: intermediate
              dtype: [None,float]
              description: The amount of stripes in the data (percent-wise)
              default: None
        artifacts_stripes_maxthickness:
              visibility: advanced
              dtype: float
              description: Defines the maximal thickness of a stripe.
              default: 3.0
              dependency:
                artifacts_stripes_percentage
        artifacts_stripes_intensity:
              visibility: advanced
              dtype: float
              description: To incorporate the change of intensity in the stripe.
              default: 0.3
              dependency:
                artifacts_stripes_percentage
        artifacts_stripes_type:
              visibility: advanced
              dtype: str
              options: [full, partial]
              description: Set the stripe type to full or partial.
              default: full
              dependency:
                artifacts_stripes_percentage
        artifacts_stripes_variability:
              visibility: advanced
              dtype: float
              description: The intensity variability of a stripe.
              default: 0.007
              dependency:
                artifacts_stripes_percentage
        artifacts_pve:
              visibility: advanced
              dtype: [None,int]
              description: the strength of partial volume effect, linked to the \
              limited resolution of the detector, try 1 or 3
              default: None
        artifacts_fresnel_distance:
              visibility: advanced
              dtype: [None,int]
              description: observation distance for fresnel propagator, e.g. 20
              default: None
        artifacts_fresnel_scale_factor:
              visibility: advanced
              dtype: float
              description: fresnel propagator sacaling
              default: 10
              dependency:
                artifacts_fresnel_distance
        artifacts_fresnel_wavelenght:
              visibility: advanced
              dtype: float
              description: fresnel propagator wavelength
              default: 0.003
              dependency:
                artifacts_fresnel_distance
        in_datasets:
              visibility: datasets
              dtype: [list[],list[str]]
              description: Default input dataset names.
              default: "['synth_proj_data']"
        out_datasets:
              visibility: datasets
              dtype: [list[],list[str]]
              description: Default out dataset names.
              default: "['synth_proj_data_artifacts']"
        """


    def citation(self):
        """
        TomoPhantom is a software package to generate 2D-4D
        analytical phantoms and their Radon transforms for various
        testing purposes.
        bibtex:
                @article{kazantsev2018tomophantom,
                  title={TomoPhantom, a software package to generate 2D-4D analytical phantoms for CT image reconstruction algorithm benchmarks},
                  author={Kazantsev, Daniil and Pickalov, Valery and Nagella, Srikanth and Pasca, Edoardo and Withers, Philip J},
                  journal={SoftwareX},
                  volume={7},
                  pages={150--155},
                  year={2018},
                  publisher={Elsevier}
                }
        endnote:
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

        doi: "10.1016/j.softx.2018.05.003"
        """
