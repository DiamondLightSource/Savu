from savu.plugins.plugin_tools import PluginTools

class CcpiRingArtefactFilterTools(PluginTools):
    """Regularization-based method for removing ring artifacts.
    """
    def define_parameters(self):
        """
        param_r:
            visibility: basic
            dtype: float
            description: The correction strength - decrease (typically in
              order of magnitude steps) to increase ring supression, or
              increase to reduce ring supression.
            default: 0.005

        num_series:
            visibility: basic
            dtype: int
            description: High aspect ration compensation (for plate-like
              objects only)
            default: 1

        param_n:
            visibility: intermediate
            dtype: int
            description: Unknown description (for plate-like objects only).
            default: 0
        """

    def citation(self):
        """
        The ring artefact removal algorithm used in this
        processing chain is taken from this work.
        bibtex:
                @inproceedings{
                titarenko2010regularization,
                title={Regularization methods for inverse problems in x-ray tomography},
                author={Titarenko, Valeriy and Bradley, Robert and Martin, Christopher and Withers, Philip J and Titarenko, Sofya},
                booktitle={Developments in X-Ray Tomography VII},
                volume={7804},
                pages={78040Z},
                year={2010},
                organization={International Society for Optics and Photonics}
                }
        endnote:
                %0 Conference Proceedings
                %T Regularization methods for inverse problems in x-ray tomography
                %A Titarenko, Valeriy
                %A Bradley, Robert
                %A Martin, Christopher
                %A Withers, Philip J
                %A Titarenko, Sofya
                %B Developments in X-Ray Tomography VII
                %V 7804
                %P 78040Z
                %D 2010
                %I International Society for Optics and Photonics
        doi: '10.1117/12.860260'
        """