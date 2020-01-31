# replaces tomobar_recon_yaml.py
from savu.plugins.plugin_info import PluginInfo

class TomoBarReconInfo(PluginInfo):
    """
    """
    def define_parameters(self):
        """
        output_size:
            visibility: advanced
            dtype: Union[int, tuple]
            description: Number of rows and columns in the reconstruction.
            default: auto

        data_fidelity:
            visibility: advanced
            dtype: str
            description: Least Squares only at the moment.
            default: LS

        data_Huber_thresh:
            visibility: advanced
            dtype: int
            description: Threshold parameter for __Huber__ data fidelity.
            default: None

        data_any_rings:
            visibility: advanced
            dtype: int
            description: a parameter to suppress various artifacts including \
                rings and streaks
            default: None

        data_any_rings_winsizes:
           visibility: advanced
           dtype: tuple
           description: half window sizes to collect background information \
               [detector, angles, num of projections]
           default: (9,7,0)

        data_any_rings_power:
            visibility: advanced
            type: float
            description: a power parameter for Huber model.
            default: 1.5
        """


    def get_bibtex(self):
        """@article{beck2009fast,
         title={A fast iterative shrinkage-thresholding algorithm for linear inverse problems},
         author={Beck, Amir and Teboulle, Marc},
         journal={SIAM journal on imaging sciences},
         volume={2},
         number={1},
         pages={183--202},
         year={2009},
         publisher={SIAM}
        }
        """


    def get_endnote(self):
        """%0 Journal Article
        %T A fast iterative shrinkage-thresholding algorithm for linear inverse problems
        %A Beck, Amir
        %A Teboulle, Marc
        %J SIAM journal on imaging sciences
        %V 2
        %N 1
        %P 183-202
        %@ 1936-4954
        %D 2009
        %I SIAM
        """

