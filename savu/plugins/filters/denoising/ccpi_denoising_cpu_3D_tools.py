from savu.plugins.plugin_tools import PluginTools

class CcpiDenoisingCpu3dTools(PluginTools):
    """Wrapper for CCPi-Regularisation Toolkit (GPU) for \
efficient 2D/3D denoising.
    """
    def define_parameters(self):
        """
        method:
             visibility: advanced
             dtype: str
             options: [ROF_TV, FGP_TV, SB_TV, NLTV, TGV, LLT_ROF, NDF, Diff4th]
             description:
               summary: The denoising method
               verbose: "Iterative methods can help to solve ill-posed \
                          inverse problems by choosing a suitable noise \
                          model for the measurement"
               options:
                   ROF_TV: Rudin-Osher-Fatemi Total Variation model
                   FGP_TV: Fast Gradient Projection Total Variation model
                   SB_TV: Split Bregman Total Variation model
                   LLT_ROF: "Lysaker, Lundervold and Tai model combined \
                     with Rudin-Osher-Fatemi"
                   NDF: "Nonlinear/Linear Diffusion model (Perona-Malik, \
                     Huber or Tukey)"
                   TGV: Total Generalised Variation
                   NLTV: Non Local Total Variation
                   DIFF4th: Fourth-order nonlinear diffusion model
             default: FGP_TV

        reg_parameter:
             visibility: basic
             dtype: float
             description:
               summary: "Regularisation (smoothing) parameter. The higher the value, the \
                 stronger the smoothing effect"
               range: Recommended between 0 and 1
             default: 0.01

        max_iterations:
             visibility: basic
             dtype: int
             description: 'Total number of regularisation iterations.'
             default: 300

        time_step:
             visibility: advanced
             dtype: int
             description: 'Time marching step, relevant for ROF_TV, LLT_ROF,\
               NDF, DIFF4th methods.'
             default: 0.001
             dependency:
                 method: [ROF_TV, LLT_ROF, NDF, DIFF4th]

        lipshitz_constant:
             visibility: advanced
             dtype: int
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
             options: [Huber, Perona, Tukey, Constr, Constrhuber]
             description:
               summary: Penalty type
               verbose: "Nonlinear/Linear Diffusion model (NDF) specific penalty \
                 type."
               options:
                 Huber: Huber
                 Perona: Perona-Malik model
                 Tukey: Tukey
             dependency:
                 method: NDF
             default: Huber

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

        """


    def get_bibtex(self):
        """@article{kazantsev2019ccpi,
        title={Ccpi-regularisation toolkit for computed tomographic image reconstruction with proximal splitting algorithms},
        author={Kazantsev, Daniil and Pasca, Edoardo and Turner, Martin J and Withers, Philip J},
        journal={SoftwareX},
        volume={9},
        pages={317--323},
        year={2019},
        publisher={Elsevier}
        }
        """


    def get_endnote(self):
        """%0 Journal Article
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
        """