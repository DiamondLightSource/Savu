
.. _savu_plugin:

What is a Savu plugin
************************

A plugin is a short program which takes a piece of data as input and manipulates
it in a certain way. Each plugin performs a specific independent task, such as correction, \
filtering or reconstruction.

Plugins are grouped into categories of similar functionality. Loaders and \
savers are two of these categories. Each process list must begin with a \
loader plugin and end with a saver plugin (hdf5 is the default), \
with at least one processing plugin in-between. The loader informs the framework \
of the data location and format along with important metadata such as shape, \
axis information, and associated patterns (e.g. sinogram, projection). \
Therefore, the choice of loader is dependent upon the format of the data.

.. note::

        Savu plugins can run on the CPU or the GPU.  If you are running the single-threaded version of Savu
        and you don't have a GPU you will be limited to CPU plugins.


.. _plugin_doc_list:

Plugin Documentation
---------------------

Below is a list of the current plugins grouped by type. You may also use the
search bar on the left to find a specific one.

.. toctree::
   :maxdepth: 2

   ../reference/plugin_documentation

