from savu.plugins.plugin_tools import PluginTools

class TomobarReconTools(PluginTools):
    """A plugin to reconstruct full-field tomographic projection data using
state-of-the-art regularised iterative algorithms from the ToMoBAR package.
ToMoBAR includes FISTA and ADMM iterative methods and depends on the ASTRA
toolbox and the CCPi RGL toolkit
    """
    def define_parameters(self):
        """

        data_fidelity:
            visibility: advanced
            dtype: str
            description: Least Squares only at the moment.
            default: LS

        data_Huber_thresh:
            visibility: advanced
            dtype: int
            description:
                summary: Threshold parameter for __Huber__ data fidelity.
                verbose: Parameter which controls the level of suppression
                 of outliers in the data
            default: None

        data_any_rings:
            visibility: hidden
            dtype: int
            description: a parameter to suppress various artifacts including
              rings and streaks
            default: None

        data_any_rings_winsizes:
           visibility: hidden
           dtype: tuple
           description: half window sizes to collect background information
             [detector, angles, num of projections]
           default: (9,7,9)
           dependency:
               data_any_rings

        data_any_rings_power:
            visibility: hidden
            dtype: float
            description: a power parameter for Huber model.
            default: 1.5
            dependency:
               data_any_rings

        data_full_ring_GH:
             visibility: advanced
             dtype: float
             description:
                summary: Regularisation variable of Group-Huber method to
                  suppress constant intensity stripes in the data to minimise
                  ring artefacts.
                verbose: Group-Huber ring removal method by Paleo and Mirone
             default: None

        data_full_ring_accelerator_GH:
             visibility: advanced
             dtype: float
             description:
                summary: Acceleration constant for Group-Huber ring removal method
                verbose: A large value can lead to divergence of the method
             default: 10.0
             dependency:
                data_full_ring_GH

        algorithm_iterations:
             visibility: basic
             dtype: int
             description:
               summary: Number of outer iterations for FISTA (default)
                  or ADMM methods.
               verbose: Less than 10 iterations for the ordered-subsets
                  iterative method (FISTA) can deliver a blurry
                  reconstruction. The suggested value is 15 iterations,
                  however the algorithm can stop prematurely based on the
                  tolerance value.
             default: 20

        algorithm_verbose:
             visibility: advanced
             dtype: bool
             description: Print iterations number and other messages
              (off by default).
             default: 'off'

        algorithm_ordersubsets:
             visibility: advanced
             dtype: int
             description:
                summary: The number of ordered-subsets to accelerate
                 image reconstruction algorithm.
                verbose: Ordered subsets number is the number of smaller
                 sets of projection data
             default: 6

        algorithm_nonnegativity:
            visibility: advanced
            dtype: str
            options: [ENABLE, DISABLE]
            description:
                summary: ENABLE or DISABLE nonnegativity constraint for
                 reconstructed image.
                options:
                    ENABLE: This enables nonnegativity constraint (meaning
                     no negative values in the reconstruction)
                    DISABLE: Reconstructed image can include negative values
            default: ENABLE

        regularisation_method:
             visibility: advanced
             dtype: str
             options: [ROF_TV, FGP_TV, PD_TV, SB_TV, LLT_ROF, NDF, TGV, NLTV, Diff4th]
             description:
               summary: The regularisation (denoising) method to stabilise
                the iterative method
               verbose: The regularised iterative methods can help to reduce
                noise and artefacts in undersampled and noisy data conditions
               options:
                   ROF_TV: Rudin-Osher-Fatemi Total Variation model
                    (piecewise-constant recovery)
                   FGP_TV: Fast Gradient Projection Total Variation model
                   PD_TV: Primal-Dual Total Variation
                   SB_TV: Split Bregman Total Variation model
                   LLT_ROF: Lysaker, Lundervold and Tai model combined
                     with Rudin-Osher-Fatemi
                   NDF: Nonlinear/Linear Diffusion model (Perona-Malik,
                     Huber or Tukey)
                   TGV: Total Generalised Variation
                   NLTV: Non Local Total Variation
                   Diff4th: Fourth-order nonlinear diffusion model
             default: FGP_TV

        regularisation_parameter:
             visibility: basic
             dtype: [float, int]
             description:
               summary: Regularisation parameter could control the level
                 of smoothing or denoising.
               verbose: Higher regularisation values lead to stronger smoothing
                 effect. If the value is too high, you will obtain a very blurry
                 reconstructed image.
               range: Recommended between 0.0001 and 0.1
             example: 'A good value to start with is {default}, {range}'
             default: 0.0001
             dependency:
                regularisation_method: not None

        regularisation_iterations:
             visibility: basic
             dtype: int
             description:
               summary: Total number of regularisation iterations.
                 The smaller the number of iterations, the smaller the effect
                 of the filtering is. A larger number will affect the speed
                 of the algorithm.
               range: Recommended value dependent upon method.
             default:
                 regularisation_method:
                   ROF_TV: 1000
                   FGP_TV: 500
                   PD_TV: 100
                   SB_TV: 100
                   LLT_ROF: 1000
                   NDF: 1000
                   Diff4th: 1000
                   TGV: 80
                   NLTV: 80
             dependency:
                regularisation_method: not None


        regularisation_device:
             visibility: advanced
             dtype: str
             description: The device for regularisation
             default: gpu
             dependency:
                regularisation_method: not None

        regularisation_PD_lip:
             visibility: advanced
             dtype: int
             description: Primal-dual TV method convergence parameter.
             default: 8
             dependency:
               regularisation_method: PD_TV

        regularisation_methodTV:
             visibility: advanced
             dtype: str
             description: 0/1 - TV specific isotropic/anisotropic choice.
             default: 0
             dependency:
               regularisation_method: [ROF_TV, FGP_TV, PD_TV, SB_TV, NLTV]

        regularisation_timestep:
             visibility: advanced
             dtype: float
             description:
               summary: Time marching parameter for convergence of explicit schemes
               verbose: the time step constant defines the speed of convergence, the larger values can lead to divergence
               range: Recommended between 0.0001 and 0.003
             default: 0.003
             dependency:
               regularisation_method: [ROF_TV, LLT_ROF, NDF, Diff4th]

        regularisation_edge_thresh:
             visibility: advanced
             dtype: float
             description:
               summary: Edge (noise) related threshold for diffusion methods
             default: 0.01
             dependency:
               regularisation_method: [NDF, Diff4th]

        regularisation_parameter2:
             visibility: advanced
             dtype: float
             description:
               summary: Regularisation (smoothing) value for LLT_ROF method
               verbose: The higher the value stronger the smoothing effect
             default: 0.005
             dependency:
               regularisation_method: LLT_ROF

        regularisation_NDF_penalty:
             visibility: advanced
             dtype: str
             options: [Huber, Perona, Tukey]
             description:
               summary: Penalty dtype
               verbose: Nonlinear/Linear Diffusion model (NDF) specific penalty
                 type.
               options:
                 Huber: Huber
                 Perona: Perona-Malik model
                 Tukey: Tukey Biweight
             dependency:
               regularisation_method: NDF
             default: Huber

        """


    def define_citations(self):
        """
        citation1:
            description: First-order optimisation algorithm for linear inverse problems
            bibtex: |
                    @article{beck2009fast,
                    title={A fast iterative shrinkage-thresholding algorithm for linear inverse problems},
                    author={Beck, Amir and Teboulle, Marc},
                    journal={SIAM journal on imaging sciences},
                    volume={2},
                    number={1},
                    pages={183--202},
                    year={2009},
                    publisher={SIAM}
                    }
            endnote: |
                    %0 Journal Article
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
            doi: "10.1016/j.jsb.2011.07.017"
        """