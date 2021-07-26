:orphan:

Distortion Correction Documentation
#################################################################

To use this plugin, users need to provide distortion coefficients which are obtained by:

1. Acquiring a dot-pattern image (Fig. 1a).

    .. figure:: ../../../files_and_images/plugin_guides/plugins/corrections/distortion_correction/fig1.jpg
       :figwidth: 90 %
       :align: center
       :figclass: align-center

       Figure 1. (a) Dot-pattern image is used for calculating distortion coefficients. (b) Result of applying the correction.

2. Using the `Discorpy <https://github.com/DiamondLightSource/discorpy>`_ or `Vounwarp <https://github.com/nghia-vo/vounwarp>`_ package for calculation.
   Following one of examples under the folder "examples" of these repositories to know how to. Referring to this
   `documentation <https://doi.org/10.5281/zenodo.1322720>`_ to know more about algorithms used to calculate
   distortion coefficients from a dot-pattern image.

**Importance notes:**

1. Distortion correction is important in tomographic applications which study small features such as pores or cracks
   as shown in Fig. 2 and Fig. 3.

    .. figure:: ../../../files_and_images/plugin_guides/plugins/corrections/distortion_correction/fig2.jpg
       :figwidth: 90 %
       :align: center
       :figclass: align-center

       Figure 2. Reconstructed image before distortion correction.

    .. figure:: ../../../files_and_images/plugin_guides/plugins/corrections/distortion_correction/fig3.jpg
       :figwidth: 90 %
       :align: center
       :figclass: align-center

       Figure 3. Reconstructed image after distortion correction.

2. To generate a single corrected sinogram, users need to provide a chunk of adjacent sinograms, i.e. by adjusting
   the "preview" parameter of a loader, as the distortion correction method uses neighbouring pixels for
   interpolation.

3. Distortion correction needs to be used in processing data from scanning techniques; which `extend the FOV of
   a parallel-beam tomography system <https://doi.org/10.1364/OE.418448>`_ such as half-acquisition scans, grid
   scans, or helical scans; because the distortion problem significantly affects the quality of stitched images.