from savu.plugins.plugin_tools import PluginTools

class BaseTomophantomLoaderTools(PluginTools):
    """A hdf5 dataset of a specified size is created at runtime using Tomophantom
    to generate synthetic data , saved with relevant meta_data to a NeXus
    file, and used as input. It recreates the behaviour of the nxtomo loader
    but with synthetic data.  The input file path passed to Savu will be ignored
    (use a dummy).
    """
    def define_parameters(self):
        """
        proj_data_dims:
              visibility: basic
              dtype: [list[float], list[]]
              description: A list specifiying the sizes of dimensions of the generated 3D \
              projection data in the following format [Angles, DetectorsY, DetectorsX].
              default: [180, 128, 160]
        axis_labels:
              visibility: basic
              dtype: [list[],list[str]]
              description: "A list of the axis labels to be associated
                with each dimension, of the form ['name1.unit1', 'name2.unit2',...]"
              default: []
        tomo_model:
              visibility: basic
              dtype: int
              description: Select a model number from the library (see TomoPhantom dat files).
              default: 13
        patterns:
              visibility: hidden
              dtype: [list[],list[str]]
              description: "A list of data access patterns e.g.
                [SINOGRAM.0c.1s.2c, PROJECTION.0s.1c.2s], where
                'c' and 's' represent core and slice dimensions
                respectively and every dimension must be
                specified."
              default: []
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
