from savu.plugins.plugin_tools import PluginTools

class MtfDeconvolutionTools(PluginTools):
    """Method to correct the point-spread-function effect. Working on raw \
    projections and flats.
    """
    def define_parameters(self):
        """
        file_path:
              visibility: basic
              dtype: [None,filepath]
              description: Path to file containing a 2D array of a MTF function.
                File formats are 'npy', or 'tif'.
              default: None

        pad_width:
              visibility: basic
              dtype: int
              description: Pad the image before the deconvolution.
              default: 128

        """

    def citation(self):
        """
        The PSF correction used in this plugin is taken
        from this work
        bibtex:
                @inproceedings{vo2019preprocessing,
                  title={Preprocessing techniques for removing artifacts in synchrotron-based tomographic images},
                  author={Vo, Nghia T and Atwood, Robert C and Drakopoulos, Michael},
                  booktitle={Developments in X-Ray Tomography XII},
                  volume={11113},
                  pages={111131I},
                  year={2019},
                  organization={International Society for Optics and Photonics}
                  publisher = {SPIE},
                  pages = {309 -- 328},
                  year = {2019},
                  doi = {10.1117/12.2530324},
                  URL = {https://doi.org/10.1117/12.2530324}
                }
        endnote:
                %0 Conference Proceedings
                %T Preprocessing techniques for removing artifacts in synchrotron-based tomographic images
                %A Vo, Nghia T
                %A Atwood, Robert C
                %A Drakopoulos, Michael
                %B Developments in X-Ray Tomography XII
                %V 11113
                %P 111131I
                %D 2019
                %I International Society for Optics and Photonics
        doi: "10.1117/12.2530324"
        """