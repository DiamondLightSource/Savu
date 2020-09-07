from savu.plugins.plugin_tools import PluginTools

class TomobarReconFully3dTools(PluginTools):
    """A Plugin to reconstruct full-field tomographic projection data
using state-of-the-art regularised iterative algorithms from
the ToMoBAR package. ToMoBAR includes FISTA and ADMM iterative
methods and depends on the ASTRA toolbox and the CCPi RGL toolkit:
https://github.com/vais-ral/CCPi-Regularisation-Toolkit.
    """
    def define_parameters(self):
        """
        output_size:
            visibility: advanced
            dtype: tuple
            description: "The dimension of the reconstructed volume
              (only X-Y dimension)."
            default: auto

        data_fidelity:
            visibility: advanced
            dtype: str
            description: Least Squares only at the moment.
            default: LS

        data_Huber_thresh:
            visibility: advanced
            dtype: int
            description: "Threshold parameter for __Huber__ data fidelity."
            default: None

        data_any_rings:
            visibility: hidden
            dtype: int
            description: "A parameter to suppress various artifacts including
              rings and streaks"
            default: None

        data_any_rings_winsizes:
            visibility: hidden
            dtype: tuple
            description: "Half window sizes to collect background information
              [detector, angles, num of projections]"
            default: (9,7,9)

        data_any_rings_power:
            visibility: hidden
            dtype: float
            description: A power parameter for Huber model.
            default: 1.5

        data_full_ring_GH:
             visibility: advanced
             dtype: str
             description: "Regularisation variable for full constant ring
               removal (GH model)."
             default: None

        data_full_ring_accelerator_GH:
            visibility: advanced
            dtype: float
            description: "Acceleration constant for GH ring removal.
               (use with care)"
            default: 10.0

        algorithm_iterations:
            visibility: basic
            dtype: int
            description:
               summary: "Number of outer iterations for FISTA (default)or ADMM methods."
               verbose: "Less than 10 iterations for the iterative method
                  (FISTA) can deliver a blurry reconstruction. The
                  suggested value is 15 iterations, however the
                  algorithm can stop prematurely based on the tolerance
                  value."
            default: 20

        algorithm_verbose:
            visibility: advanced
            dtype: bool
            description: "Print iterations number and other messages (off by default)."
            default: 'off'

        algorithm_ordersubsets:
            visibility: advanced
            dtype: int
            description: "The number of ordered-subsets to accelerate reconstruction."
            default: 6

        algorithm_nonnegativity:
            visibility: advanced
            dtype: str
            options: [ENABLE, DISABLE]
            description:
                summary: ENABLE or DISABLE nonnegativity constraint.
            default: ENABLE

        regularisation_method:
            visibility: advanced
            dtype: str
            options: [ROF_TV, FGP_TV, PD_TV, SB_TV, LLT_ROF, NDF, TGV,
             NLTV, Diff4th]
            description:
                summary: The denoising method
                verbose: "Iterative methods can help to solve ill-posed
                          inverse problems by choosing a suitable noise
                          model for the measurement"
                options:
                   ROF_TV: Rudin-Osher-Fatemi Total Variation model
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
            dtype: float
            description:
                summary: "Regularisation parameter. The higher the value, the
                  stronger the smoothing effect"
                range: Recommended between 0 and 1
            default: 0.0001

        regularisation_iterations:
            visibility: basic
            dtype: int
            description: "Total number of regularisation iterations.
              The smaller the number of iterations, the smaller the
              effect of the filtering is. A larger number will affect
              the speed of the algorithm."
            default: 80

        regularisation_device:
            visibility: advanced
            dtype: str
            description: The device for regularisation
            default: gpu

        regularisation_PD_lip:
            visibility: advanced
            dtype: int
            description: "Primal-dual parameter for convergence."
            default: 8
            dependency:
                regularisation_method: PD_TV

        regularisation_methodTV:
             visibility: advanced
             dtype: str
             description: "0/1 - TV specific isotropic/anisotropic choice."
             default: 0
             dependency:
               regularisation_method: [ROF_TV, FGP_TV, SB_TV, NLTV]

        regularisation_timestep:
             visibility: advanced
             dtype: float
             dependency:
               regularisation_method: [ROF_TV, LLT_ROF, NDF, Diff4th]
             description:
               summary: Time marching parameter
               range: Recommended between 0.0001 and 0.003
             default: 0.003

        regularisation_edge_thresh:
             visibility: advanced
             dtype: float
             dependency:
               regularisation_method: [NDF, Diff4th]
             description:
               summary: "Edge (noise) related parameter"
             default: 0.01

        regularisation_parameter2:
             visibility: advanced
             dtype: float
             dependency:
               regularisation_method: LLT_ROF
             description:
               summary: "Regularisation (smoothing) value"
               verbose: The higher the value stronger the smoothing effect
             default: 0.005

        regularisation_NDF_penalty:
             visibility: advanced
             dtype: str
             options: [Huber, Perona, Tukey]
             description:
               summary: Penalty dtype
               verbose: "Nonlinear/Linear Diffusion model (NDF) specific
                 penalty type."
               options:
                 Huber: Huber
                 Perona: Perona-Malik model
                 Tukey: Tukey
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