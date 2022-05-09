
Iterative plugins API
*********************

Introduction / What is it for?
==============================

The iterative functionality in Savu provides a way to run a plugin (or a group
of plugins) multiple times in sequence, without the need to manually create
multiple instances of the plugin(s) in the Savu configurator. In other words,
this feature provides the ability to easily define iterative loops in Savu
process lists.

This can be useful for neatly representing in Savu different kinds of processing
pipelines that involve repeated applications of a single plugin, or multiple
plugins, such as :ref:`emulating-3d-denoising`, or :ref:`iterative-alignment`.

Setting iterative plugins
=========================

Adding iterative loops
----------------------

An iterative loop can be defined in a process list by providing a few pieces of
information to the Savu configurator:

* the plugin indices that mark the start and end of the iterative loop

* the number of iterations to perform

This can be done with the command :code:`iterate --set a b n`, where

* :code:`a` is the index of the plugin where the loop should start

* :code:`b` is the index of the plugin where the loop should end

* :code:`n` is the number of iterations to perform

For example, to iterate a single plugin with index 3 a total of 5 times, run
:code:`iterate --set 3 3 5`.

As another example, to iterate from plugin index 3 to plugin index 4 a total of
5 times, run :code:`iterate --set 3 4 5`.

Removing iterative loops
------------------------

Iterative loops are numbered inside the configurator starting from 1. This
labelling can be viewed with the command :code:`iterate`.

To remove a loop (or multiple loops), pass the number label for the loops to the
command :code:`iterate --remove`.

For example, to remove a loop with the label 1, run :code:`iterate
--remove 1`.

As another example, to remove two loops, one with label 1 and another with
label 2, run :code:`iterate --remove 1 2`.

Additionally, all loops in the process list can be removed by running
:code:`iterate --remove` and then confirming the action when prompted.

Viewing all iterative loops
---------------------------

As mentioned above, all loops and their associated information (number label,
start index, end index, number of iterations) can be viewed with the
:code:`iterate` command.

Examples:
=========

Here we provide two examples how iterative plugins can be used in Savu.

.. _emulating-3d-denoising:

Emulating 3D denoising
--------------------------------------------------------------------------------------------------------------------------

One can build a case where 2D denoising methods changing slicing patterns alternatingly in iterations thus enabling a much smoother recovery from noise. In image bellow we demonstrate how plugins no. 3 and 4 can be converted to be iterative. Using command `iterate --set 3 4 10`, plugins no. 3 and 4 have different slicing patterns and
locked in an iterative loop of 10 (global) iterations. The result of denoising in this case is more consistent in every spatial
direction than using one dimension. This filtering, although 2D, emulates 3D denoising.

.. figure:: iterative_ex1.png
   :figwidth: 100%
   :align: left
   :figclass: align-left

.. figure:: iterative_ex2.png
   :figwidth: 100%
   :align: left
   :figclass: align-left

.. _iterative-alignment:

Iterative alignment reconstruction algorithm
-------------------------------------------------------

This approach to reconstruct misaligned data is based on an iterative refinement with re-projection in order to perform a simultaneous reconstruction and alignment, see the paper: `Rapid alignment of nanotomography data using joint iterative reconstruction and reprojection <https://www.nature.com/articles/s41598-017-12141-9>`_.

With iterative plugins API it is possible to build the following iterative pipeline which will enable the iterative alignment algorithm. Plugin no. 3 performs re-projection of the reconstructed image,
no.4 initialises a registration method to perform alignment of the re-projected data with the original raw data in projection space and no.5  reconstructs the corrected projection data.
Note that different reconstruction algorithms can be used to reconstruct the corrected data, e.g. it could be the FBP algorithm of the `AstraReconGpu` plugin or a regulairised iterative reconstruction of
the `ToMoBAR` package (`TomobarRecon3d` plugin). Notably the latter converges significantly faster and delivers a superior reconstruction, hence recommended if the computation time is not the essence (see the images).

.. figure:: iterative_ex3.png
   :figwidth: 60%
   :align: left
   :figclass: align-left

.. figure:: iterative_ex4.png
   :figwidth: 100%
   :align: left
   :figclass: align-left

Two implementations of iterative alignment
==========================================

One implementation is based on the implementation in tomopy, where the
projections are shifted. The other implementation is a variation, based on the
idea of using the x and y projection shifts to translate the source/detector(?)
during the reconstruction process that occurs in the iterative loop.

# TODO: come up with a name for "the other implementation". Will refer to it as
# "the Savu implementation" for now

Each of the two different implementations are better suited for data depending
on a few different attributes of the data, so the given misaligned projection
data will advise which implementation should be used on a case-by-case basis.

Choosing which implementation to use
------------------------------------

As a rule-of-thumb, if the estimated magnitude of the misalignment is large
(approximately > 60 pixels(?)) then the tomopy implementation is more suitable,
and if they're smaller (<= 60 pixels(?)) then the "Savu implementation" is
preferred.

# TODO: maybe give some advice on how to estimate the magnitude of the shifts in
# data, to help with choosing an implementation?

A single parameter for the :code:`Projection2dAlignment` plugin called
:code:`registration` can be set to choose which implementation is used.
:code:`True` applies the tomopy implementation, and :code:`False` applies the
"Savu implementation".

# TODO: for all examples below, show:
# - process list w/ :code:`n` iterations in it
# - the input data
# - maybe the aligned projections at the end of the iterations
# - the final reconstruction from the aligned projections

Tomopy implementation
---------------------

# TODO: explanation of why this implementation is sometimes preferred (large
# shifts requires large padding, which breaks Savu/becomes very slow, and this
# implementation can avoid these issues)?

Synthetic data example
######################

Real data example
#################

"Savu implementation"
---------------------

# TODO: explanation of why this implementation is sometimes preferred?

Synthetic data example
######################

Real data example
#################
