from savu.plugins.plugin_tools import PluginTools

class SimpleReconTools(PluginTools):
    """A Plugin to apply a simple reconstruction with no dependancies
    """

    def get_bibtex(self):
        """@article{kak2002principles,
              title={Principles of computerized tomographic imaging},
              author={Kak, Avinash C and Slaney, Malcolm and Wang, Ge},
              journal={Medical Physics},
              volume={29},
              number={1},
              pages={107--107},
              year={2002},
              publisher={Wiley Online Library}
            }
        """


    def get_endnote(self):
        """%0 Journal Article
            %T Principles of computerized tomographic imaging
            %A Kak, Avinash C
            %A Slaney, Malcolm
            %A Wang, Ge
            %J Medical Physics
            %V 29
            %N 1
            %P 107-107
            %@ 0094-2405
            %D 2002
            %I Wiley Online Library
        """

