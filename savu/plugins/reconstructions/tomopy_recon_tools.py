from savu.plugins.plugin_tools import PluginTools

class TomopyReconTools(PluginTools):
    """A wrapper to the tomopy reconstruction library. Extra keywords not
required for the chosen algorithm will be ignored.
    """
    def define_parameters(self):
        """
        algorithm:
            visibility: intermediate
            dtype: tuple
            description: "The reconstruction algorithm (art|bart|fbp|gridrec|
              mlem|osem|ospml_hybrid|ospml_quad|pml_hybrid|pml_quad|sirt)."
            default: gridrec

        filter_name:
            visibility: intermediate
            dtype: str
            description: "Valid for fbp|gridrec, options - none|shepp|cosine|
              hann|hamming|ramlak|parzen|butterworth)."
            default: ramlak
            options: [none,shepp,cosine,hann,hamming,ramlak,parzen,butterworth]
            dependencies:
                algorithm: [fbp, gridrec]

        reg_par:
            visibility: intermediate
            dtype: float
            description: "Regularization parameter for smoothing, valid for
              ospml_hybrid|ospml_quad|pml_hybrid|pml_quad."
            default: 0.0
            dependencies:
                algortihm: [ospml_hybrid, ospml_quad, pml_hybrid, pml_quad]

        n_iterations:
            visibility: intermediate
            dtype: int
            description: "Number of iterations - only valid for iterative
              algorithms."
            default: 1

        init_vol:
            visibility: hidden
            dtype: int
            description: Not an option.
            default: None

        centre_pad:
            visibility: hidden
            dtype: int
            description: Not an option.
            default: None

        """


    def get_bibtex(self):
        """
        @article{gursoy2014tomopy,
        title={TomoPy: a framework for the analysis of synchrotron tomographic data},
        author={G{\"u}rsoy, Doga and De Carlo, Francesco and Xiao, Xianghui and Jacobsen, Chris},
        journal={Journal of synchrotron radiation},
        volume={21},
        number={5},
        pages={1188--1193},
        year={2014},
        publisher={International Union of Crystallography}}
        """


    def get_endnote(self):
        """
        %0 Journal Article
        %T TomoPy: a framework for the analysis of synchrotron tomographic data
        %A G{\"u}rsoy, Doga
        %A De Carlo, Francesco
        %A Xiao, Xianghui
        %A Jacobsen, Chris
        %J Journal of synchrotron radiation
        %V 21
        %N 5
        %P 1188-1193
        %@ 1600-5775
        %D 2014
        %I International Union of Crystallography
        """