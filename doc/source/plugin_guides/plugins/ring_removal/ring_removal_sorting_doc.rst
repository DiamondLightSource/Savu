:orphan:

Ring Removal Sorting Documentation
#################################################################

This plugin is used to remove full and partial ring artifacts. It works particularly well to remove partial rings.

.. figure:: ../../../files_and_images/plugin_guides/plugins/ring_removal/ring_removal_sorting/fig1.jpg
   :figwidth: 90 %
   :align: center
   :figclass: align-center

   Figure 1. Sinogram (a) and reconstructed image (b) before the plugin is applied.

.. figure:: ../../../files_and_images/plugin_guides/plugins/ring_removal/ring_removal_sorting/fig2.jpg
   :figwidth: 90 %
   :align: center
   :figclass: align-center

   Figure 2. Sinogram (a) and reconstructed image (b) after the plugin is applied.

Explanation about the method and how to use is `here <https://sarepy.readthedocs.io/toc/section3_1/section3_1_1.html#sorting-based-approach>`_
(note that ring artifacts in a reconstructed image corresponding to stripe artifacts in the sinogram image).

**Important note:**

This plugin should *not* be used after a plugin which blurs an image such as PaganinFilter or FresnelFilter.
