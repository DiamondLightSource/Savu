from savu.plugins.plugin_tools import PluginTools

class TomobarReconCpuTools(PluginTools):
    """A CPU Plugin to reconstruct full-field tomographic projection data using
state-of-the-art regularised iterative algorithms from the ToMoBAR package.
ToMoBAR includes FISTA and ADMM iterative methods and depends on the ASTRA
toolbox and the CCPi RGL toolkit.
    """

    def define_parameters(self):
        """
        data_fidelity:
            visibility: advanced
            dtype: str
            description: Data fidelity, choose LS, PWLS, SWLS or KL.
            default: LS

        data_Huber_thresh:
            visibility: advanced
            dtype: [None,int]
            description: Threshold parameter for __Huber__ data fidelity.
            default: None

        data_beta_SWLS:
            visibility: advanced
            dtype: float
            description: A parameter for stripe-weighted model.
            default: 0.1

        data_full_ring_GH:
             visibility: advanced
             dtype: [None,str]
             description: Regularisation variable for full constant
               ring removal (GH model).
             default: None

        data_full_ring_accelerator_GH:
             visibility: advanced
             dtype: float
             description: Acceleration constant for GH ring removal. (use with care)
             default: 10.0

        algorithm_iterations:
             visibility: basic
             dtype: int
             description:
               summary: Number of outer iterations for FISTA (default)or
                 ADMM methods.
               verbose: Less than 10 iterations for the iterative method
                  (FISTA) can deliver a blurry reconstruction. The
                  suggested value is 15 iterations, however the
                  algorithm can stop prematurely based on the tolerance
                  value.
             default: 15

        algorithm_verbose:
             visibility: advanced
             dtype: str
             description: Print iterations number and other messages
               (off by default).
             options: [on,off]
             default: 'off'

        algorithm_mask:
             visibility: advanced
             dtype: float
             description: set to 1.0 to enable a circular mask diameter
               or < 1.0 to shrink the mask.
             default: 1.0

        algorithm_ordersubsets:
             visibility: advanced
             dtype: int
             description: The number of ordered-subsets to accelerate
               reconstruction.
             default: 6

        algorithm_nonnegativity:
            visibility: advanced
            dtype: str
            options: [ENABLE, DISABLE]
            description:
                summary: ENABLE or DISABLE nonnegativity constraint.
            default: ENABLE

        regularisation_method:
             visibility: intermediate
             dtype: str
             options: [ROF_TV, FGP_TV, PD_TV, SB_TV, LLT_ROF, NDF,
              TGV, NLTV, Diff4th]
             description:
               summary: The regularisation (denoising) method to stabilise
                the iterative recovery
               verbose: Iterative methods can help to solve ill-posed
                          inverse problems by choosing a suitable noise
                          model for the measurement
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
               summary: Regularisation parameter. The higher the value, the
                 stronger the smoothing effect
               range: Recommended between 1e-06 and 1e-04
             default: 5e-06

        regularisation_iterations:
             visibility: intermediate
             dtype: int
             description:
               summary: Total number of regularisation iterations.
                 The smaller the number of iterations, the smaller the effect
                 of the filtering is. A larger number will affect the speed
                 of the algorithm.
               range: Recommended value dependent upon method.
             default:
                 regularisation_method:
                   ROF_TV: 300
                   FGP_TV: 100
                   PD_TV: 100
                   SB_TV: 100
                   LLT_ROF: 300
                   NDF: 300
                   Diff4th: 300
                   TGV: 150
                   NLTV: 30
             dependency:
                regularisation_method

        regularisation_PD_lip:
             visibility: advanced
             dtype: int
             description: Primal-dual parameter for convergence.
             default: 8
             dependency:
               regularisation_method: PD_TV

        regularisation_methodTV:
             visibility: advanced
             dtype: int
             description: 0/1 - TV specific isotropic/anisotropic choice.
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
               summary: Edge (noise) related parameter
             default: 0.01

        regularisation_parameter2:
             visibility: advanced
             dtype: float
             dependency:
               regularisation_method: LLT_ROF
             description:
               summary: Regularisation (smoothing) value
               verbose: The higher the value stronger the smoothing effect
             default: 0.005

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
                 Tukey: Tukey
             dependency:
               regularisation_method: NDF
             default: Huber

        """


    def citation(self):
        """
        First-order optimisation algorithm for linear inverse problems
        bibtex:
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
        endnote:
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


    def citation2(self):
        """
        Rudin-Osher-Fatemi explicit PDE minimisation method
        for smoothed Total Variation regulariser
        bibtex:
                @article{rudin1992nonlinear,
                  title={Nonlinear total variation based noise removal algorithms},
                  author={Rudin, Leonid I and Osher, Stanley and Fatemi, Emad},
                  journal={Physica D: nonlinear phenomena},
                  volume={60},
                  number={1-4},
                  pages={259--268},
                  year={1992},
                  publisher={North-Holland}
                }
        endnote:
                %0 Journal Article
                %T Nonlinear total variation based noise removal algorithms
                %A Rudin, Leonid I
                %A Osher, Stanley
                %A Fatemi, Emad
                %J Physica D: nonlinear phenomena
                %V 60
                %N 1-4
                %P 259-268
                %@ 0167-2789
                %D 1992
                %I North-Holland
        doi: "10.1016/0167-2789(92)90242-F"
        dependency:
            regularisation_method: ROF_TV
        """

    def citation3(self):
        """
        Fast-Gradient-Projection algorithm for
        Total Variation regulariser
        bibtex:
                @article{beck2009fast,
                  title={Fast gradient-based algorithms for constrained total variation image denoising and deblurring problems},
                  author={Beck, Amir and Teboulle, Marc},
                  journal={IEEE transactions on image processing},
                  volume={18},
                  number={11},
                  pages={2419--2434},
                  year={2009},
                  publisher={IEEE}
                }
        endnote:
                %0 Journal Article
                %T Fast gradient-based algorithms for constrained total variation image denoising and deblurring problems
                %A Beck, Amir
                %A Teboulle, Marc
                %J IEEE transactions on image processing
                %V 18
                %N 11
                %P 2419-2434
                %@ 1057-7149
                %D 2009
                %I IEEE
        doi: "10.1109/TIP.2009.2028250"
        dependency:
            regularisation_method: FGP_TV
        """

    def citation4(self):
        """
        The Split Bregman approach for Total Variation
        regulariser
        bibtex:
               @article{goldstein2009split,
                  title={The split Bregman method for L1-regularized problems},
                  author={Goldstein, Tom and Osher, Stanley},
                  journal={SIAM journal on imaging sciences},
                  volume={2},
                  number={2},
                  pages={323--343},
                  year={2009},
                  publisher={SIAM}
                }
        endnote:
                %0 Journal Article
                %T The split Bregman method for L1-regularized problems
                %A Goldstein, Tom
                %A Osher, Stanley
                %J SIAM journal on imaging sciences
                %V 2
                %N 2
                %P 323-343
                %@ 1936-4954
                %D 2009
                %I SIAM
        doi: "10.1137/080725891"
        dependency:
            regularisation_method: SB_TV
        """

    def citation5(self):
        """
        Total generalized variation regulariser for
        piecewise-smooth recovery
        bibtex:
               @article{bredies2010total,
                  title={Total generalized variation},
                  author={Bredies, Kristian and Kunisch, Karl and Pock, Thomas},
                  journal={SIAM Journal on Imaging Sciences},
                  volume={3},
                  number={3},
                  pages={492--526},
                  year={2010},
                  publisher={SIAM}
                }
        endnote:
                %0 Journal Article
                %T Total generalized variation
                %A Bredies, Kristian
                %A Kunisch, Karl
                %A Pock, Thomas
                %J SIAM Journal on Imaging Sciences
                %V 3
                %N 3
                %P 492-526
                %@ 1936-4954
                %D 2010
                %I SIAM
        doi: "10.1137/080725891"
        dependency:
            regularisation_method: TGV
        """

    def citation6(self):
        """
        Combination for ROF model and LLT for
        piecewise-smooth recovery
        bibtex:
               @article{kazantsev2017model,
                title={Model-based iterative reconstruction using higher-order regularization of dynamic synchrotron data},
                author={Kazantsev, Daniil and Guo, Enyu and Phillion, AB and Withers, Philip J and Lee, Peter D},
                journal={Measurement Science and Technology},
                volume={28},
                number={9},
                pages={094004},
                year={2017},
                publisher={IOP Publishing}
                }
        endnote:
                %0 Journal Article
                %T Model-based iterative reconstruction using higher-order regularization of dynamic synchrotron data
                %A Kazantsev, Daniil
                %A Guo, Enyu
                %A Phillion, AB
                %A Withers, Philip J
                %A Lee, Peter D
                %J Measurement Science and Technology
                %V 28
                %N 9
                %P 094004
                %@ 0957-0233
                %D 2017
                %I IOP Publishing
        doi: "10.1088/1361-6501"
        dependency:
            regularisation_method: LLT_ROF
        """

    def citation7(self):
        """
        Nonlinear or linear duffison as a regulariser
        bibtex:
               @article{perona1990scale,
                  title={Scale-space and edge detection using anisotropic diffusion},
                  author={Perona, Pietro and Malik, Jitendra},
                  journal={IEEE Transactions on pattern analysis and machine intelligence},
                  volume={12},
                  number={7},
                  pages={629--639},
                  year={1990},
                  publisher={IEEE}}
        endnote:
                %0 Journal Article
                %T Scale-space and edge detection using anisotropic diffusion
                %A Perona, Pietro
                %A Malik, Jitendra
                %J IEEE Transactions on pattern analysis and machine intelligence
                %V 12
                %N 7
                %P 629-639
                %@ 0162-8828
                %D 1990
                %I IEEE
        doi: "10.1109/34.56205"
        dependency:
            regularisation_method: NDF
        """

    def citation8(self):
        """
        Anisotropic diffusion of higher order for
        piecewise-smooth recovery
        bibtex:
               @article{hajiaboli2011anisotropic,
                title={An anisotropic fourth-order diffusion filter for image noise removal},
                author={Hajiaboli, Mohammad Reza},
                journal={International Journal of Computer Vision},
                volume={92},
                number={2},
                pages={177--191},
                year={2011},
                publisher={Springer}
                }
        endnote:
                %0 Journal Article
                %T An anisotropic fourth-order diffusion filter for image noise removal
                %A Hajiaboli, Mohammad Reza
                %J International Journal of Computer Vision
                %V 92
                %N 2
                %P 177-191
                %@ 0920-5691
                %D 2011
                %I Springer
        doi: "10.1007/s11263-010-0330-1"
        dependency:
            regularisation_method: Diff4th
        """

    def citation9(self):
        """
        Nonlocal discrete regularization on weighted
        graphs - a framework for image and manifold processing
        bibtex:
                @article{elmoataz2008nonlocal,
                  title={Nonlocal discrete regularization on weighted graphs: a framework for image and manifold processing},
                  author={Elmoataz, Abderrahim and Lezoray, Olivier and Bougleux, S{\'e}bastien},
                  journal={IEEE transactions on Image Processing},
                  volume={17},
                  number={7},
                  pages={1047--1060},
                  year={2008},
                  publisher={IEEE}
                }
        endnote:
                %0 Journal Article
                %T Nonlocal discrete regularization on weighted graphs, a framework for image and manifold processing
                %A Elmoataz, Abderrahim
                %A Lezoray, Olivier
                %A Bougleux, Sebastien
                %J IEEE transactions on Image Processing
                %V 17
                %N 7
                %P 1047-1060
                %@ 1057-7149
                %D 2008
                %I IEEE
        doi: '10.1109/TIP.2008.924284'
        dependency:
            regularisation_method: NLTV

        """
