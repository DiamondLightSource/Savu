from savu.plugins.plugin_tools import PluginTools


class TomoPhantomTools(PluginTools):
    """A plugin for TomoPhantom software which generates synthetic phantoms
and projection data (2D from Phantom2DLibrary.dat and 3D from
Phantom3DLibrary.dat)
    """

    def define_parameters(self):
        """
        geom_model:
              visibility: basic
              dtype: int
              description: Select a model (integer) from the library (see TomoPhantom files).
              default: 1
        geom_model_size:
              visibility: basic
              dtype: int
              description: Set the size of the phantom.
              default: 256
        geom_projections_total:
              visibility: intermediate
              dtype: int
              description: The total number of projections.
              default: 360
        geom_detectors_horiz:
              visibility: intermediate
              dtype: int
              description: The size of _horizontal_ detectors.
              default: 300
        artifacts_noise_type:
              visibility: intermediate
              dtype: str
              description: Set the noise type, Poisson or Gaussian.
              default: Poisson
        artifacts_noise_sigma:
              visibility: intermediate
              dtype: int
              description: Define noise amplitude.
              default: 5000
        artifacts_misalignment_maxamplitude:
              visibility: intermediate
              dtype: [None,int]
              description: Incorporate misalignment into projections (in pixels).
              default: None
        artifacts_zingers_percentage:
              visibility: intermediate
              dtype: [None,float]
              description: Add broken pixels to projections, e.g. 0.25.
              default: None
        artifacts_stripes_percentage:
              visibility: intermediate
              dtype: [None,float]
              description: The amount of stripes in the data, e.g. 1.0.
              default: None
        artifacts_stripes_maxthickness:
              visibility: intermediate
              dtype: float
              description: Defines the maximal thickness of a stripe.
              default: 3.0
        artifacts_stripes_intensity:
              visibility: intermediate
              dtype: float
              description: To incorporate the change of intensity in the stripe.
              default: 0.3
        artifacts_stripes_type:
              visibility: intermediate
              dtype: str
              description: Set the stripe type between full and partial.
              default: full
        artifacts_stripes_variability:
              visibility: intermediate
              dtype: float
              description: The intensity variability of a stripe.
              default: 0.007
        out_datasets:
              visibility: datasets
              dtype: [list[],list[str]]
              description: Default out dataset names.
              default: "['tomo', 'model']"

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