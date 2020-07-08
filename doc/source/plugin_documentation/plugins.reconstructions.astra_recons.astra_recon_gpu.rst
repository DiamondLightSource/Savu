Astra Recon Gpu
#################################################################

Description
--------------------------

A Plugin to run the astra reconstruction
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        res_norm:
            visibility: basic
            dtype: int
            description: Output the residual norm at each iteration
              (Error in the solution - iterative solvers only)
            default: False
            dependency:
              algorithm: [SIRT_CUDA, SART_CUDA, CGLS_CUDA]
        algorithm:
            visibility: basic
            dtype: str
            options: [FBP_CUDA, SIRT_CUDA, SART_CUDA, CGLS_CUDA, FP_CUDA, BP_CUDA]
            description:
                summary: Reconstruction type
                options:
                  FBP_CUDA: Filtered Backprojection
                  SIRT_CUDA: Simultaneous Iterative Reconstruction Technique
                  SART_CUDA: Simultaneous Algebraic Reconstruction Technique
                  CGLS_CUDA: Conjugate Gradient Least Squares
                  FP_CUDA:
                  BP_CUDA:
                  SIRT3D_CUDA:
                  CGLS3D_CUDA:
            default: FBP_CUDA
        FBP_filter:
            visibility: basic
            dtype: str
            options:  [none,
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
                blackman|nuttall,
                blackman-harris,
                blackman-nuttall,
                flat-top,
                kaiser,
                parzen]
            description:
              summary: The FBP reconstruction filter type
              options:
                none:
                ram-lak:
                shepp-logan:
                cosine:
                hamming:
                hann:
                tukey:
                lanczos:
                triangular:
                gaussian:
                barlett-hann:
                blackman|nuttall:
                blackman-harris:
                blackman-nuttall:
                flat-top:
                kaiser:
                parzen:
            default: 'ram-lak'

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
