from savu.plugins.plugin_tools import PluginTools

class BaseAstraVectorReconTools(PluginTools):
    """A Plugin to perform Astra toolbox reconstruction using vector
geometry
    """
    def define_parameters(self):
        """
        n_iterations:
            visibility: basic
            dtype: int
            description: Number of iterations to perform
            default: 1
            dependency:
              algorithm: [SIRT_CUDA, SART_CUDA, CGLS_CUDA, CGLS3D_CUDA, SIRT3D_CUDA]
        outer_pad:
             visibility: intermediate
             dtype: [bool, float]
             description: 'Pad the sinogram width to fill the
               reconstructed volume for asthetic purposes. Choose
               from True (defaults to sqrt(2)), False or
               float <= 2.1.'
             warning: This will increase the size of the data and
               the time to compute the reconstruction. Only available
               for selected algorithms and will be ignored otherwise.
             default: False
        centre_pad:
              visibility: intermediate
              dtype: [bool, float]
              description: Pad the sinogram to centre it in order
                to fill the reconstructed volume ROI for asthetic
                purposes.
              warning: This will significantly increase the size of
                the data and the time to compute the reconstruction)
              default: False              
        """

    def citation1(self):
        """
        The tomography reconstruction algorithm used in this processing
        pipeline is part of the ASTRA Toolbox
        bibtex:
                @article{van2016fast,
                title={Fast and flexible X-ray tomography using the ASTRA toolbox},
                author={Van Aarle, Wim and Palenstijn, Willem Jan and Cant, Jeroen and Janssens, Eline and Bleichrodt, Folkert and Dabravolski, Andrei and De Beenhouwer, Jan and Batenburg, K Joost and Sijbers, Jan},
                journal={Optics express},
                volume={24},
                number={22},
                pages={25129--25147},
                year={2016},
                publisher={Optical Society of America}
                }
        endnote:
                %0 Journal Article
                %T Fast and flexible X-ray tomography using the ASTRA toolbox
                %A Van Aarle, Wim
                %A Palenstijn, Willem Jan
                %A Cant, Jeroen
                %A Janssens, Eline
                %A Bleichrodt, Folkert
                %A Dabravolski, Andrei
                %A De Beenhouwer, Jan
                %A Batenburg, K Joost
                %A Sijbers, Jan
                %J Optics express
                %V 24
                %N 22
                %P 25129-25147
                %@ 1094-4087
                %D 2016
                %I Optical Society of America
        doi: "10.1364/OE.24.025129"
        """

    def citation2(self):
        """
        The tomography reconstruction algorithm used in this processing
        pipeline is part of the ASTRA Toolbox
        bibtex:
                @article{van2015astra,
                title={The ASTRA Toolbox: A platform for advanced algorithm development in electron tomography},
                author={Van Aarle, Wim and Palenstijn, Willem Jan and De Beenhouwer, Jan and Altantzis, Thomas and Bals, Sara and Batenburg, K Joost and Sijbers, Jan},
                journal={Ultramicroscopy},
                volume={157},
                pages={35--47},
                year={2015},
                publisher={Elsevier}
                }
        endnote:
                %0 Journal Article
                %T The ASTRA Toolbox: A platform for advanced algorithm development in electron tomography
                %A Van Aarle, Wim
                %A Palenstijn, Willem Jan
                %A De Beenhouwer, Jan
                %A Altantzis, Thomas
                %A Bals, Sara
                %A Batenburg, K Joost
                %A Sijbers, Jan
                %J Ultramicroscopy
                %V 157
                %P 35-47
                %@ 0304-3991
                %D 2015
                %I Elsevier
        doi: "10.1364/OE.24.025129"
        """
    