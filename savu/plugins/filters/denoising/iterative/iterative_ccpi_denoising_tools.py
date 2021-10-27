from savu.plugins.plugin_tools import PluginTools

class IterativeCcpiDenoisingTools(PluginTools):
    """A wrapper for CCPi-Regularisation Toolkit (CPU) for efficient 2D denoising with changing patterns
    """
    def define_parameters(self):
        """
        plugin_iterations:
             visibility: basic
             dtype: int
             description:
               summary: "The number of plugin iterations"
             default: 5

        method:
             visibility: advanced
             dtype: str
             options: [ROF_TV, PD_TV, FGP_TV, SB_TV, NLTV, TGV, LLT_ROF, NDF, Diff4th]
             description:
               summary: The denoising method
               verbose: "Variational denoising algorithms can be used to filter
                          the data while preserving the important features"
               options:
                   ROF_TV: Rudin-Osher-Fatemi Total Variation model
                   PD_TV: Primal-Dual Total variation model
                   FGP_TV: Fast Gradient Projection Total Variation model
                   SB_TV: Split Bregman Total Variation model
                   LLT_ROF: "Lysaker, Lundervold and Tai model combined
                     with Rudin-Osher-Fatemi"
                   NDF: "Nonlinear/Linear Diffusion model (Perona-Malik,
                     Huber or Tukey)"
                   TGV: Total Generalised Variation
                   NLTV: Non Local Total Variation
                   Diff4th: Fourth-order nonlinear diffusion model
             default: FGP_TV

        reg_parameter:
             visibility: basic
             dtype: float
             description:
               summary: "The regularisation (smoothing) parameter. The higher the value, the
                 stronger the smoothing effect"
               range: Recommended between 0 and 0.001
             default: 0.00001

        max_iterations:
            visibility: basic
            dtype: int
            description:
                summary: Total number of regularisation iterations.  The
                    smaller the number of iterations, the smaller the effect of
                    the filtering is.  A larger number will affect the speed of
                    the algorithm.
                range: Recommended value dependent upon method.
            default:
                method:
                    ROF_TV: 2000
                    FGP_TV: 500
                    PD_TV: 500
                    SB_TV: 100
                    LLT_ROF: 2000
                    NDF: 2000
                    Diff4th: 1000
                    TGV: 500
                    NLTV: 5

        time_step:
             visibility: advanced
             dtype: float
             dependency:
               regularisation_method: [ROF_TV, LLT_ROF, NDF, Diff4th]
             description:
               summary: Time marching parameter for convergence of explicit schemes
               verbose: the time step constant defines the speed of convergence, the larger values can lead to divergence
               range: Recommended between 0.0001 and 0.003
             default: 0.003

        lipshitz_constant:
            visibility: advanced
            dtype: float
            description: TGV method, Lipshitz constant.
            default: 12
            dependency:
                method: TGV

        alpha1:
            visibility: advanced
            dtype: float
            description: 'TGV method, parameter to control the 1st-order term.'
            default: 1.0
            dependency:
                method: TGV

        alpha0:
            visibility: advanced
            dtype: float
            description: 'TGV method, parameter to control the 2nd-order term.'
            default: 2.0
            dependency:
                method: TGV

        reg_parLLT:
            visibility: advanced
            dtype: float
            dependency:
                method: LLT_ROF
            description: 'LLT-ROF method, parameter to control the 2nd-order term.'
            default: 0.05

        penalty_type:
            visibility: advanced
            dtype: str
            options: [huber, perona, tukey, constr, constrhuber]
            description:
                summary: Penalty type
                verbose: "Nonlinear/Linear Diffusion model (NDF) specific penalty
                   type."
                options:
                    huber: Huber
                    perona: Perona-Malik model
                    tukey: Tukey
                    constr:
                    constrhuber:
            dependency:
                method: NDF
            default: huber

        edge_par:
            visibility: advanced
            dtype: float
            dependency:
                method: [NDF, Diff4th]
            description: 'NDF and Diff4th methods, noise magnitude parameter.'
            default: 0.01

        tolerance_constant:
            visibility: advanced
            dtype: float
            description: Tolerance constant to stop iterations earlier.
            default: 0.0

        pattern:
            visibility: advanced
            dtype: str
            description: Pattern to apply this to.
            default: 'VOLUME_XZ'
        """

    def citation1(self):
        """
        The CCPi-Regularisation toolkit provides a set of
        variational regularisers (denoisers) which can be embedded in
        a plug-and-play fashion into proximal splitting methods for
        image reconstruction. CCPi-RGL comes with algorithms that can
        satisfy various prior expectations of the reconstructed object,
        for example being piecewise-constant or piecewise-smooth nature.
        bibtex:
                @article{kazantsev2019ccpi,
                title={Ccpi-regularisation toolkit for computed tomographic image reconstruction with proximal splitting algorithms},
                author={Kazantsev, Daniil and Pasca, Edoardo and Turner, Martin J and Withers, Philip J},
                journal={SoftwareX},
                volume={9},
                pages={317--323},
                year={2019},
                publisher={Elsevier}
                }
        endnote:
                %0 Journal Article
                %T Ccpi-regularisation toolkit for computed tomographic image reconstruction with proximal splitting algorithms
                %A Kazantsev, Daniil
                %A Pasca, Edoardo
                %A Turner, Martin J
                %A Withers, Philip J
                %J SoftwareX
                %V 9
                %P 317-323
                %@ 2352-7110
                %D 2019
                %I Elsevier
        doi: "10.1016/j.softx.2019.04.003"
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
            method: ROF_TV
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
            method: FGP_TV
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
            method: SB_TV
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
            method: TGV
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
            method: LLT_ROF
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
            method: NDF
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
            method: Diff4th
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
            method: NLTV

        """
