How to view the Savu output
----------------------------


.. _dawn:

In DAWN
^^^^^^^
Open a new terminal window and type:

    >>> module load dawn
    >>> dawn &

Choose the Data Browsing perspective and click on File -> open, navigate to an output folder and click on
the .nxs file.

.. warning:: The DAWN module must be loaded in a separate terminal as it will reset relevant paths.


In Avizo
^^^^^^^^

Start avizo

    >>> module load avizo
    >>> avizo

In Avizo GUI, Click on Open Data /(File->Open Data). This should show a dialog box with list of output data
entries. To view final output select entry/final_result_tomo/data and press OK button. This will load the data.

1. 2D view

To view 2D slices, Select the data, right click and a pop up will be shown as below. Select Ortho Slice and Click ok button to show a 2D slice.
    .. image:: ../files_and_images/2dview.jpg

2. 3D view

To view 3D volume, Select the data, right click on it and a pop up will be shown as below. Select Volume Rendering and Click OK button to show a 3D volume.
    .. image:: ../files_and_images/3dview.jpg


