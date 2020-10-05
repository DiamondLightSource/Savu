from savu.plugins.plugin_tools import PluginTools

class VoCenteringIterativeTools(PluginTools):
    """A plugin to calculate the centre of rotation using the Vo Method
    """
    def define_parameters(self):
        """
        ratio:
             visibility: intermediate
             dtype: float
             description: The ratio between the size of object and FOV of the camera
             default: 0.5
        row_drop:
             visibility: intermediate
             dtype: int
             description: Drop lines around vertical center of the mask.
             default: 20
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
        expand_by:
             visibility: advanced
             dtype: int
             description: The number of pixels to expand the search region by
               on each iteration
             default: 5
        boundary_distance:
             visibility: advanced
             dtype: int
             description: Accepted distance of minima from the boundary of
               the listshift in the coarse search.
             default: 3
        preview:
             visibility: intermediate
             dtype: int_list
             description: 'A slice list of required frames (sinograms) to use in
               the calculation of the centre of rotation (this will not reduce the data
               size for subsequent plugins).'
             default: '[]'
        datasets_to_populate:
             visibility: advanced
             dtype: list
             description: A list of datasets which require this information
             default: '[]'
        out_datasets:
             visibility: datasets
             dtype: list
             description: The default names
             default: "['cor_raw','cor_fit', 'reliability']"
        start_pixel:
             visibility: advanced
             dtype: int
             description: 'The approximate centre. If value is None, take the
               value from .nxs file else set to image centre.'
             default: None
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
                publisher={Optical Society of America}}
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