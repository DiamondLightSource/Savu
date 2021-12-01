from savu.plugins.plugin_tools import PluginTools

class Centering360Tools(PluginTools):
    """A plugin to calculate the centre of rotation
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
        win_width:
             visibility: basic
             dtype: int
             description: Width of window used for finding the overlap area
             default: 100
        side:
             visibility: basic
             dtype: [None,int]
             description: Overlap size. "None" corresponding to fully automated
               determination. "0" corresponding to the left side.
                "1" corresponding to the right side.
             default: None
             options: [None, 1, 0]
        denoise:
             visibility: intermediate
             dtype: bool
             description: Apply the gaussian filter if True
             default: True
        norm:
             visibility: intermediate
             dtype: bool
             description: Apply the normalisation if True
             default: True
        use_overlap:
             visibility: intermediate
             dtype: bool
             description: Use the combination of images in the overlap area for calculating
               correlation coefficients if True.
             default: True


        broadcast_method:
             visibility: intermediate
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


        """

    def citation(self):
        """
        The center of rotation for this reconstruction was calculated
        automatically using the method described in this work
        bibtex:
                @article{Vo:21,
                author = {Nghia T. Vo and Robert C. Atwood and Michael Drakopoulos and Thomas Connolley},
                journal = {Opt. Express},
                keywords = {Digital image processing; Fluorescence tomography; Image processing; Image registration; Phase contrast; Phase retrieval},
                number = {12},
                pages = {17849--17874},
                publisher = {OSA},
                title = {Data processing methods and data acquisition for samples larger than the field of view in parallel-beam tomography},
                volume = {29},
                month = {Jun},
                year = {2021},
                url = {http://www.osapublishing.org/oe/abstract.cfm?URI=oe-29-12-17849},
                doi = {10.1364/OE.418448},
                abstract = {Parallel-beam tomography systems at synchrotron facilities have limited field of view (FOV) determined by the available beam size and detector system coverage. Scanning the full size of samples bigger than the FOV requires various data acquisition schemes such as grid scan, 360-degree scan with offset center-of-rotation (COR), helical scan, or combinations of these schemes. Though straightforward to implement, these scanning techniques have not often been used due to the lack of software and methods to process such types of data in an easy and automated fashion. The ease of use and automation is critical at synchrotron facilities where using visual inspection in data processing steps such as image stitching, COR determination, or helical data conversion is impractical due to the large size of datasets. Here, we provide methods and their implementations in a Python package, named Algotom, for not only processing such data types but also with the highest quality possible. The efficiency and ease of use of these tools can help to extend applications of parallel-beam tomography systems.},
                }

        endnote:
                %0 Journal Article
                %T Data processing methods and data acquisition for samples larger than the field of view in parallel-beam tomography
                %A Vo, Nghia T
                %A Atwood, Robert C
                %A Drakopoulos, Michael
                %A Connolley, Thomas
                %J Optics Express
                %V 29
                %N 12
                %P 17849-17874
                %@ 1094-4087
                %D 2021
                %I Optical Society of America
        doi: "https://doi.org/10.1364/OE.418448"

        """
