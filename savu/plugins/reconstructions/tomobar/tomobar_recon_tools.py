from savu.plugins.plugin_tools import PluginTools

# Lines 15-248 of this file are used for the yaml file template example
# doc/source/dev_guides/dev_plugin_tools/dev_param_ex.rst

class TomobarReconTools(PluginTools):
    """A GPU plugin to reconstruct full-field tomographic projection data using
state-of-the-art regularised iterative algorithms from the ToMoBAR package.
ToMoBAR includes FISTA and ADMM iterative methods and depends on the ASTRA
toolbox and the CCPi RGL toolkit. https://github.com/vais-ral/CCPi-Regularisation-Toolkit.
    """
    def define_parameters(self):
        """
        output_size:
            visibility: advanced
            dtype: [list,int.str]
            description: Number of rows and columns in the reconstruction.
            default: auto

        data_fidelity:
            visibility: advanced
            dtype: str
            description: Data fidelity, choose LS, PWLS, SWLS or KL.
            default: LS

        data_Huber_thresh:
            visibility: advanced
            dtype: [None,int]
            description:
                summary: Threshold parameter for Huber data fidelity.
                verbose: Parameter which controls the level of suppression
                 of outliers in the data
            default: None

        data_beta_SWLS:
            visibility: advanced
            dtype: float
            description: A parameter for stripe weighted model.
            default: 0.1

        data_full_ring_GH:
             visibility: advanced
             dtype: [None,float]
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

        algorithm_mask:
             visibility: advanced
             dtype: float
             description: Set to 1.0 to enable a circular mask diameter
               or less than 1.0 to shrink the mask.
             default: 1.0

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
             options: [ROF_TV, FGP_TV, PD_TV, SB_TV, LLT_ROF, NDF, TGV, NLTV, Diff4th, None]
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
             dtype: float
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
                regularisation_method

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
                regularisation_method

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
