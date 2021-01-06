
What is a Process list
------------------------

Savu is a framework that does nothing if you run it on its own.  It requires a process list, passed to it
at runtime along with the data, to detail the processing steps it should follow.  A Savu process list is
created using the Savu configurator tool, which stacks together plugins chosen from a repository. Each plugin
performs a specific independent task, such as correction, filtering, reconstruction.  For a list of available
plugins see `plugin API <file:///home/qmm55171/Documents/Git/git_repos/Savu/doc/build/plugin_autosummary.html>`_.

Plugins are grouped into categories of similar functionality.  Loaders and savers are two of these categories and each
process list must begin with a loader plugin and optionally end with a saver plugin (hdf5 is the default), with at
least one processing plugin in-between.  The loader informs the framework of the data location and format along
with important metadata such as shape, axis information, and associated patterns (e.g. sinogram, projection).
Therefore, the choice of loader is dependent upon the format of the data.

.. note:: Savu plugins can run on the CPU or the GPU.  If you are running the single-threaded version of Savu
          and you don't have a GPU you will be limited to CPU plugins.

