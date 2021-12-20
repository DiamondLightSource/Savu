from savu.plugins.plugin_tools import PluginTools

class AstraReconGpuTools(PluginTools):
    """A Plugin to run the astra reconstruction
    """
    def define_parameters(self):
        """
        res_norm:
            visibility: basic
            dtype: [int,bool]
            description: Output the residual norm at each iteration
              (Error in the solution)
            default: False
            dependency:
              algorithm: [SIRT_CUDA, SART_CUDA, CGLS_CUDA, CGLS3D_CUDA, SIRT3D_CUDA]
        algorithm:
            visibility: basic
            dtype: str
            options: [FBP_CUDA, SIRT_CUDA, SART_CUDA, CGLS_CUDA,
              BP_CUDA, SIRT3D_CUDA, CGLS3D_CUDA]
            description:
                summary: Reconstruction type
                options:
                  FBP_CUDA: Filtered Backprojection Method
                  SIRT_CUDA: Simultaneous Iterative Reconstruction Technique
                  SART_CUDA: Simultaneous Algebraic Reconstruction Technique
                  CGLS_CUDA: Conjugate Gradient Least Squares
                  BP_CUDA: Backward Projection
                  SIRT3D_CUDA: Simultaneous Iterative Reconstruction Technique 3D
                  CGLS3D_CUDA: Conjugate Gradient Least Squares 3D
            default: FBP_CUDA
        FBP_filter:
            visibility: intermediate
            dtype: str
            options: [none,
                ram-lak,
                shepp-logan,
                cosine,
                hamming,
                hann,
                tukey,
                lanczos,
                triangular,
                gaussian,
                barlett-hann,
                blackman,
                nuttall,
                blackman-harris,
                blackman-nuttall,
                flat-top,
                kaiser,
                parzen]
            description:
              summary: The FBP reconstruction filter type
              options:
                none: No filtering
                ram-lak: Ram-Lak or ramp filter
                shepp-logan: Multiplies the Ram-Lak filter by a sinc function
                cosine: Multiplies the Ram-Lak filter by a cosine function
                hamming: Multiplies the Ram-Lak filter by a hamming window
                hann: Multiplies the Ram-Lak filter by a hann window
                tukey:
                lanczos:
                triangular:
                gaussian:
                barlett-hann:
                blackman:
                nuttall:
                blackman-harris:
                blackman-nuttall:
                flat-top:
                kaiser:
                parzen:
            default: 'ram-lak'
            dependency:
                algorithm: [FBP_CUDA]
        outer_pad:
             dependency:
               algorithm: [FBP_CUDA, BP_CUDA]
        centre_pad:
             dependency:
               algorithm: [FBP_CUDA, BP_CUDA]               
        """


    def citation(self):
        """
        The tomography reconstruction algorithm used in this processing
        pipeline is part of the ASTRA Toolbox
        bibtex:
                @article{palenstijn2011performance,
                  title={Performance improvements for iterative electron tomography reconstruction using graphics processing units (GPUs)},
                  author={Palenstijn, WJ and Batenburg, KJ and Sijbers, J},
                  journal={Journal of structural biology},
                  volume={176},
                  number={2},
                  pages={250--253},
                  year={2011},
                  publisher={Elsevier}
                }
        endnote:
                %0 Journal Article
                %T Performance improvements for iterative electron tomography reconstruction using graphics processing units (GPUs)
                %A Palenstijn, WJ
                %A Batenburg, KJ
                %A Sijbers, J
                %J Journal of structural biology
                %V 176
                %N 2
                %P 250-253
                %@ 1047-8477
                %D 2011
                %I Elsevier
        doi: "10.1016/j.jsb.2011.07.017"
        """
