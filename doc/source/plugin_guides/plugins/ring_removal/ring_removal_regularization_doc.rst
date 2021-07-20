:orphan:

Ring Removal Regularization Documentation
#################################################################

This plugin is used to remove full ring artifacts.

Explanation about the method and how to use is `here <https://sarepy.readthedocs.io/toc/section3_1/section3_1_2.html#sarepy.prep.stripe_removal_former.remove_stripe_based_regularization>`_
(note that ring artifacts in a reconstructed image corresponding to stripe artifacts in the sinogram image).

**Important note:**

This plugin should *not* be used after a plugin which blurs an image such as PaganinFilter or FresnelFilter.
