How to install Savu on a PC
=================================

Savu-lite is designed to run on a local PC workstation. The main functionality of Savu is preserved with Savu-lite except the MPI part.
Currently Savu-lite is built for Python 3.7 with Numpy 1.15. To install it you'll need a clean conda environment.

**1a: Installation of Savu-lite from the savu-dep conda channel**

*Probably the easiest method since you'll be installing the pre-built version from the conda channel.*

1. Install miniconda (preferably 4.6.14 which comes with Python 3.7) and activate it

2. >>> conda create -n savu

3. >>> conda activate savu

4. >>> conda install savu-lite -c conda-forge -c savu-dep -c ccpi -c astra-toolbox/label/dev

**1b: Installation of Savu-lite using the explicit list of packages**

*This method requires cloning the repository and then installing all the dependencies from the explicit list.*
*Then Savu-lite is installed into the environment.*

1. Get the explicit list file from `HERE <https://github.com/DiamondLightSource/Savu/blob/master/install/savu_lite37/spec-savu_lite_latest.txt>`_
2. >>> conda install --yes --name savu --file spec-savu_lite_latest.txt
3. From the main Savu folder run *python setup.py install*
