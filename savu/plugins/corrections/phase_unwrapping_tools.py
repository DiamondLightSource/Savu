from savu.plugins.plugin_tools import PluginTools

class PhaseUnwrappingTools(PluginTools):
    """A plugin to unwrap a phase-image retrieved by another phase retrieval
    method (e.g. ptychography). Note that values of the input have to be
    in the range of [-pi; pi]"""
    
    def define_parameters(self):
        """
        n_iterations:
            visibility: basic
            dtype: int
            description: Number of iterations to perform.
            default: 4

        pattern:
            visibility: basic
            dtype: str
            description: Data processing pattern.
            options: [PROJECTION, SINOGRAM]
            default: PROJECTION
        """

    def citation(self):
        """
        The code is the implementation of the work taken from the following paper.

        bibtex:
            @article{Martinez-Carranza:17,
            author = {Juan Martinez-Carranza and Konstantinos Falaggis and Tomasz Kozacki},
            journal = {Appl. Opt.},
            number = {25},
            pages = {7079--7088},
            publisher = {OSA},
            title = {Fast and accurate phase-unwrapping algorithm based on the transport of intensity equation},
            volume = {56},
            month = {Sep},
            year = {2017},
            url = {http://www.osapublishing.org/ao/abstract.cfm?URI=ao-56-25-7079},
            doi = {10.1364/AO.56.007079}}

        endnote:
            TI  - Fast and accurate phase-unwrapping algorithm based on the transport of intensity equation
            AU  - Martinez-Carranza, Juan
            AU  - Falaggis, Konstantinos
            AU  - Kozacki, Tomasz
            PB  - OSA
            PY  - 2017
            JF  - Applied Optics
            VL  - 56
            IS  - 25
            SP  - 7079
            EP  - 7088
            UR  - http://www.osapublishing.org/ao/abstract.cfm?URI=ao-56-25-7079
            DO  - 10.1364/AO.56.007079

        doi: 10.1364/AO.56.007079
        """
