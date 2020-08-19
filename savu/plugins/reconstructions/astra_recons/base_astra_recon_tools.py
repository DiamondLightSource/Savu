from savu.plugins.plugin_tools import PluginTools

class BaseAstraReconTools(PluginTools):
    """A Plugin to perform Astra toolbox reconstruction
    """
    def define_parameters(self):
        """
        n_iterations:
            visibility: basic
            dtype: int
            description: Number of Iterations is only valid for iterative algorithms
            default: 1

        """


    def get_citation(self):
        """
        citation1:
            description: The tomography reconstruction algorithm used in this processing
              pipeline is part of the ASTRA Toolbox
            bibtex: |
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
            endnote: |
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

        citation2:
            description: The tomography reconstruction algorithm used in this processing
              pipeline is part of the ASTRA Toolbox
            bibtex: |
                    @article{van2015astra,
                    title={The ASTRA Toolbox: A platform for advanced algorithm development in electron tomography},
                    author={Van Aarle, Wim and Palenstijn, Willem Jan and De Beenhouwer, Jan and Altantzis, Thomas and Bals, Sara and Batenburg, K Joost and Sijbers, Jan},
                    journal={Ultramicroscopy},
                    volume={157},
                    pages={35--47},
                    year={2015},
                    publisher={Elsevier}
                    }
            endnote: |
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