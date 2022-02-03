from savu.plugins.plugin_tools import PluginTools


class DistortionCorrectionTools(PluginTools):
    """A plugin to apply radial distortion correction.
    """

    def define_parameters(self):
        """
        polynomial_coeffs:
              visibility: basic
              dtype: list
              description: Parameters of the radial distortion
              default: [1.0, 0.0e-6, 0.0e-8, 0.0e-11, 0.0e-15]
        center_from_top:
              visibility: basic
              dtype: float
              description: The centre of distortion in pixels from the top
                of the image.
              default: 1080.0
        center_from_left:
              visibility: basic
              dtype: float
              description: The centre of distortion in pixels from the left
                of the image.
              default: 1280.0
        file_path:
              visibility: basic
              dtype: [None, filepath, str]
              description: Path to the text file having distortion
                coefficients. Set to None for manually inputing.
              default: None
        crop_edges:
              visibility: basic
              dtype: int
              description: 'When applied to previewed/cropped data, the
                result may contain zeros around the edges, which can be
                removed by cropping the edges by a specified number of pixels'
              default: 0

        """

    def citation(self):
        """
        The distortion correction used in this processing chain is taken
        from this work.
        bibtex:
                @article{vo2015radial,
                  title={Radial lens distortion correction with sub-pixel accuracy for X-ray micro-tomography},
                  author={Vo, Nghia T and Atwood, Robert C and Drakopoulos, Michael},
                  journal={Optics express},
                  volume={23},
                  number={25},
                  pages={32859--32868},
                  year={2015},
                  publisher={Optical Society of America}
                }
        endnote:
                %0 Journal Article
                %T Radial lens distortion correction with sub-pixel accuracy for X-ray micro-tomography
                %A Vo, Nghia T
                %A Atwood, Robert C
                %A Drakopoulos, Michael
                %J Optics express
                %V 23
                %N 25
                %P 32859-32868
                %@ 1094-4087
                %D 2015
                %I Optical Society of America
        doi: "10.1364/OE.23.032859"
        """
