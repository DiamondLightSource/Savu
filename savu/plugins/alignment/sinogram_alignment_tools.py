from savu.plugins.plugin_tools import PluginTools

class SinogramAlignmentTools(PluginTools):
    """The centre of mass of each row is determined and then a sine function
    fit through these to determine the centre of rotation.  The residual
    between each centre of mass and the sine function is then used to align
    each row.
    """

    def define_parameters(self):
        """
        threshold:
              visibility: basic
              dtype: [None,str]
              description: e.g. a.b will set all values above a to b.
              default: None
        p0:
              visibility: basic
              dtype: list[float,float,float]
              description: Initial guess for the parameters of
                scipy.optimize.curve_fit.
              default: [1, 1, 1]
        type:
              visibility: intermediate
              dtype: str
              description: Either centre_of_mass or shift, with the latter
                  requiring ProjectionVerticalAlignment prior to this plugin.
              default: centre_of_mass
              options: [centre_of_mass, shift]

        """

    def citation(self):
        u"""
        The Tomographic filtering performed in this processing
        chain is derived from this work.
        bibtex:
                @article{price2015chemical,
                title={Chemical imaging of single catalyst particles with scanning $\mu$-XANES-CT and $\mu$-XRF-CT},
                author={Price, SWT and Ignatyev, K and Geraki, K and Basham, M and Filik, J and Vo, NT and Witte, PT and Beale, AM and Mosselmans, JFW},
                journal={Physical Chemistry Chemical Physics},
                volume={17},
                number={1},
                pages={521--529},
                year={2015},
                publisher={Royal Society of Chemistry}}
        endnote:
                %0 Journal Article
                %T Chemical imaging of single catalyst particles with scanning \u03BC-XANES-CT and \u03BC-XRF-CT
                %A Price, SWT
                %A Ignatyev, K
                %A Geraki, K
                %A Basham, M
                %A Filik, J
                %A Vo, NT
                %A Witte, PT
                %A Beale, AM
                %A Mosselmans, JFW
                %J Physical Chemistry Chemical Physics
                %V 17
                %N 1
                %P 521-529
                %D 2015
                %I Royal Society of Chemistry
        doi: "10.1039/c4cp04488f"

        """
