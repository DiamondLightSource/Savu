# coding=utf-8

from savu.plugins.plugin_tools import PluginTools

class TomopyReconTools(PluginTools):
    """A wrapper to the tomopy reconstruction library.
    """
    def define_parameters(self):
        """
        algorithm:
            visibility: basic
            dtype: str
            description: The reconstruction algorithm
            default: gridrec
            options: [art, bart, fbp, gridrec, mlem, osem, ospml_hybrid,
                      ospml_quat, pml_hybrid, pml_quad, sirt]

        filter_name:
            visibility: intermediate
            dtype: [None, str]
            description: Name of the filter for analytic reconstruction
            default: ramlak
            options: [None,shepp,cosine,hann,hamming,ramlak,parzen,butterworth]
            dependency:
                algorithm: [fbp, gridrec]

        reg_par:
            visibility: intermediate
            dtype: float
            description: Regularization parameter for smoothing
            default: 0.0
            dependency:
                algorithm: [ospml_hybrid, ospml_quad, pml_hybrid, pml_quad]

        n_iterations:
            visibility: basic
            dtype: int
            description: Number of iterations.
            default: 1
            dependency:
                algorithm: [art, bart, mlem, osem, ospml_hybrid,
                            ospml_quad, pml_hybrid, pml_quad, sirt]

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
             dependency:
               algorithm: [fbp, gridrec]

        init_vol:
            visibility: hidden
            dtype: [None,int]
            description: Not an option.
            default: None

        """

    def citation(self):
        """
        An algorithm from the TomoPy framework is used to
        perform the reconstruction in this processing pipeline.
        bibtex:
                @article{gursoy2014tomopy,
                title={TomoPy: a framework for the analysis of synchrotron tomographic data},
                author={Gürsoy, Doga and De Carlo, Francesco and Xiao, Xianghui and Jacobsen, Chris},
                journal={Journal of synchrotron radiation},
                volume={21},
                number={5},
                pages={1188--1193},
                year={2014},
                publisher={International Union of Crystallography}
                }
        endnote:
                %0 Journal Article
                %T TomoPy: a framework for the analysis of synchrotron tomographic data
                %A Gürsoy, Doga
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
        doi: "10.1107/S1600577514013939"
        """