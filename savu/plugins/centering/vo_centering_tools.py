from savu.plugins.plugin_tools import PluginTools

class VoCenteringTools(PluginTools):
    """A plugin to calculate the centre of rotation using the Vo method
    """
    def define_parameters(self):
        """
        preview:
             visibility: basic
             dtype: preview
             description: A slice list of required frames (sinograms) to use in
               the calculation of the centre of rotation (this will not reduce
               the data size for subsequent plugins).
             default: '[]'
             example: 'The typical three dimensional data structure is
                [angles, detY, detZ], e.g. for sinogram choose [:,sliceNo,:]
                [angles, detZ, detY]. If the data is four dimensional, include
                a time parameter.'
        start_pixel:
             visibility: intermediate
             dtype: [int,None]
             description: The estimated centre of rotation. If value is None,
               use the horizontal centre of the image.
             default: 'None'
        search_area:
             visibility: basic
             dtype: list[float,float]
             description: Search area around the estimated centre of rotation
             default: [-50, 50]
        ratio:
             visibility: intermediate
             dtype: float
             description: The ratio between the size of a sample and the field
                of view of a camera
             default: 0.5
        search_radius:
             visibility: intermediate
             dtype: int
             description: Use for fine searching
             default: 6
        step:
             visibility: intermediate
             dtype: float
             description: Step of fine searching
             default: 0.5
        datasets_to_populate:
             visibility: intermediate
             dtype: [list[],list[str]]
             description: A list of datasets which require this information
             default: []
        out_datasets:
             visibility: datasets
             dtype: [list[],list[str]]
             description: The default names
             default: "['cor_preview', 'cor_broadcast']"
        broadcast_method:
             visibility: advanced
             dtype: str
             options: [median, mean, nearest, linear_fit]
             description:
               summary: Method of broadcasting centre values calculated
                 from preview slices to full dataset.
               options:
                   median:
                   mean:
                   nearest:
                   linear_fit:
             default: median
        row_drop:
             visibility: advanced
             dtype: int
             description: Drop lines around vertical center of the mask
             default: 20
        average_radius:
             visibility: advanced
             dtype: int
             description: Averaging sinograms around a required sinogram to
               improve signal-to-noise ratio
             default: 5
        """

    def citation(self):
        """
        The center of rotation for this reconstruction was calculated
        automatically using the method described in this work
        bibtex:
                @article{vo2014reliable,
                title={Reliable method for calculating the center of rotation in parallel-beam tomography},
                author={Vo, Nghia T and Drakopoulos, Michael and Atwood, Robert C and Reinhard, Christina},
                journal={Optics express},
                volume={22},
                number={16},
                pages={19078--19086},
                year={2014},
                publisher={Optical Society of America}
                }
        endnote:
                %0 Journal Article
                %T Reliable method for calculating the center of rotation in parallel-beam tomography
                %A Vo, Nghia T
                %A Drakopoulos, Michael
                %A Atwood, Robert C
                %A Reinhard, Christina
                %J Optics express
                %V 22
                %N 16
                %P 19078-19086
                %@ 1094-4087
                %D 2014
                %I Optical Society of America
        doi: "https://doi.org/10.1364/OE.22.019078"

        """
