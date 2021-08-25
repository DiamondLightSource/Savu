Introduction
------------

Tomography data collected at Diamond has, in recent years, been processed using the Tomo Recon GPU
cluster-based code available through DAWN.  A steady increase in the popularity of tomographic imaging,
due to improvements in data acquisition and computer technology, has led to a broadening of the range of
tomographic experiments, and their complexity, across multiple fields.

In full-field tomography, where the whole region-of-interest is irradiated by the beam simultaneously,
time-resolved imaging is becoming increasingly popular.  In mapping tomography, where a thin beam of
X-rays is translated and rotated across the region of interest, multi-modal data collection is common and
incorporates a variety of measurements, such as X-ray absorption, diffraction and fluorescence.

This wide range of experimental requirements leads to a wider range of software processing requirements.
Savu, developed in the Data Analysis Group at Diamond Light Source Ltd., is the new tomography data
processing tool that has been developed to allow greater flexibility in tomography data processing. Custom
process lists are passed to Savu at runtime to enable processing to be tailored to a specific experimental
setup.  The framework is capable of processing multiple, n-dimensional, very large datasets, and is written
in Python to allow easy integration of new functionality, allowing researchers and beam line staff greater
flexibility in integrating new, cutting-edge processing techniques.

A quick comparison of the old and new tomography software is given in the table below.

+-------------------+---------------------------------------+----------------------------------------------+
|                   |            Tomo Recon                 |                      Savu                    |
+===================+=======================================+==============================================+
|    Data type      |     Full-field tomography data        |   Full-field and mapping tomography data     |
+-------------------+---------------------------------------+----------------------------------------------+
|  Data dimensions  |                 3-D                   |                     N-D                      |
+-------------------+---------------------------------------+----------------------------------------------+
|   Data format     |          Nxtomo NEXUS format          |      Multiple formats (any possible)         |
+-------------------+---------------------------------------+----------------------------------------------+
|  Output format    |                 tiff                  | Multiple formats (hdf5 - tiff coming soon)   |
+-------------------+---------------------------------------+----------------------------------------------+
|     Data size     |             Limited by RAM            |        No RAM limit (uses parallel hdf5)     |
+-------------------+---------------------------------------+----------------------------------------------+
| Datasets per run  |             One dataset               |           Multiple datasets                  |
+-------------------+---------------------------------------+----------------------------------------------+
|   Data slicing    |            Sinogram only              |       Flexible (e.g sinogram/projection)     |
+-------------------+---------------------------------------+----------------------------------------------+
|    Processing     | Fixed: correction, ring removal, FBP  |        Custom: Tailored process lists        |
+-------------------+---------------------------------------+----------------------------------------------+
| New functionality |            No integration             |                Easy integration              |
+-------------------+---------------------------------------+----------------------------------------------+

