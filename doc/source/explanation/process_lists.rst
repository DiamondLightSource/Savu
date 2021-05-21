
What is a Process list
------------------------

Savu is a framework that does nothing if you run it on its own.  It requires a process list, passed to it
at runtime along with the data, to detail the processing steps it should follow.  A Savu process list is
created using the Savu configurator tool, which stacks together :ref:`'plugins'<savu_plugin>` chosen from a
repository. Each plugin performs a specific independent task, such as correction, filtering, reconstruction.
For a list of available plugins see `plugin API <file:///home/qmm55171/Documents/Git/git_repos/Savu/doc/build/plugin_autosummary.html>`_.

