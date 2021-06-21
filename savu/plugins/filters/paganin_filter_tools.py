from savu.plugins.plugin_tools import PluginTools

class PaganinFilterTools(PluginTools):
    """A plugin to apply the Paganin filter (for denoising or contrast
    enhancement) on projections.
    """
    def define_parameters(self):
        """
        Ratio:
              visibility: basic
              dtype: float
              description: Ratio of delta/beta.
              default: 250.0
        Energy:
              visibility: basic
              dtype: float
              description: Beam energy in keV.
              default: 53.0
        Distance:
              visibility: basic
              dtype: float
              description: Distance from sample to detector. Unit is metre.
              default: 1.0
        Resolution:
              visibility: basic
              dtype: float
              description: Pixel size. Unit is micron.
              default: 1.28
        Padtopbottom:
              visibility: intermediate
              dtype: int
              description: Pad to the top and bottom of projection.
              default: 100
        Padleftright:
              visibility: intermediate
              dtype: int
              description: Pad to the left and right of projection.
              default: 100
        Padmethod:
              visibility: intermediate
              dtype: str
              description: Numpy pad method.
              default: edge
        increment:
              visibility: intermediate
              dtype: float
              description: Increment all values by this amount before taking the
                log.
              default: 0.0
        """

    def config_warn(self):
        """The 'log' parameter in the reconstruction should be set to
        FALSE.

        Previewing a subset of sinograms will alter the result, due
        to the global nature of this filter. If this is necessary, ensure they
        are consecutive.
        """

    def citation(self):
        """
        The contrast enhancement used in this processing chain is taken
        from this work.
        bibtex:
                @article{paganin2002simultaneous,
                title={Simultaneous phase and amplitude extraction from a single defocused image of a homogeneous object},
                author={Paganin, David and Mayo, Sheridan C and Gureyev, Tim E and Miller, Peter R and Wilkins, Steve W},
                journal={Journal of microscopy},
                volume={206},
                number={1},
                pages={33--40},
                year={2002},
                publisher={Wiley Online Library}
                }
        endnote:
                %0 Journal Article
                %T Simultaneous phase and amplitude extraction from a single defocused image of a homogeneous object
                %A Paganin, David
                %A Mayo, Sheridan C
                %A Gureyev, Tim E
                %A Miller, Peter R
                %A Wilkins, Steve W
                %J Journal of microscopy
                %V 206
                %N 1
                %P 33-40
                %@ 0022-2720
                %D 2002
                %I Wiley Online Library
        doi: "10.1046/j.1365-2818.2002.01010.x"
        """