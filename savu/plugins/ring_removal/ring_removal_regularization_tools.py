from savu.plugins.plugin_tools import PluginTools

class RingRemovalRegularizationTools(PluginTools):
    """Regularization-based method working in the sinogram space to remove ring
    artifacts.
    """
    def define_parameters(self):
        """
        alpha:
            visibility: basic
            dtype: float
            description: The correction strength. Smaller is stronger.
            default: 0.005
        number_of_chunks:
            visibility: basic
            dtype: int
            description: Divide the sinogram to many chunks of rows.
            default: 1
        """

    def citation(self):
        """
        The code of ring removal is the implementation
        of the work of Sofya Titarenko et al. taken from this paper
        bibtex:
                @article{titarenko2010analytical,
                  title={An analytical formula for ring artefact suppression in X-ray tomography},
                  author={Titarenko, Sofya and Withers, Philip J and Yagola, Anatoly},
                  journal={Applied Mathematics Letters},
                  volume={23},
                  number={12},
                  pages={1489--1495},
                  year={2010},
                  publisher={Elsevier}
                }
        endnote:
                %0 Journal Article
                %T An analytical formula for ring artefact suppression in X-ray tomography
                %A Titarenko, Sofya
                %A Withers, Philip J
                %A Yagola, Anatoly
                %J Applied Mathematics Letters
                %V 23
                %N 12
                %P 1489-1495
                %@ 0893-9659
                %D 2010
                %I Elsevier

        doi: "10.1016/j.aml.2010.08.022"
        """