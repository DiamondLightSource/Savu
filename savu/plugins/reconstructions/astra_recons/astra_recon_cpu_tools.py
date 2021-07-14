from savu.plugins.plugin_tools import PluginTools

class AstraReconCpuTools(PluginTools):
    """A Plugin to run the astra reconstruction
    """
    def define_parameters(self):
        """
        algorithm:
            visibility: basic
            dtype: str
            options: [FBP,SIRT,SART,ART,CGLS,BP]
            description:
              summary: Reconstruction type
              options:
                FBP: Filtered Backprojection Method
                SIRT: Simultaneous Iterative Reconstruction Technique
                SART: Simultaneous Algebraic Reconstruction Technique
                ART: Iterative Reconstruction Technique
                CGLS: Conjugate Gradient Least Squares
                BP: Back Projection
            default: FBP
        projector:
            visibility: intermediate
            dtype: str
            options: [line, strip, linear]
            description:
              summary: Set astra projector
              options:
                line: 'The weight of a ray/pixel pair is given by the length
                  of the intersection of the pixel and the ray, considered
                  as a zero-thickness line.'
                strip: 'The weight of a ray/pixel pair is given by the area
                  of the intersection of the pixel and the ray, considered
                  as a strip with the same width as a detector pixel.'
                linear: 'Linear interpolation between the two nearest volume
                  pixels of the intersection of the ray and the column/row.'
            default: line
        outer_pad:
             dependency:
               algorithm: [FBP, BP]
        centre_pad:
             dependency:
               algorithm: [FBP, BP]
        """
