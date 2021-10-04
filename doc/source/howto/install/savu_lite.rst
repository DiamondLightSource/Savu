.. |miniconda| replace:: :download:`miniconda <https://repo.anaconda.com/miniconda/Miniconda3-4.6.14-Linux-x86_64.sh>`
.. |savu_conda| replace:: :download:`savu_conda_file <https://github.com/DiamondLightSource/Savu/blob/master/install/savu_lite37/spec-savu_lite_latest.txt>`

How to install Savu on a PC (Unix)
===================================

Savu-lite is designed to run on a local PC workstation with Unix-based OS. The main functionality of Savu is preserved with Savu-lite except the MPI part.
Currently Savu-lite is built for Python 3.7 with Numpy 1.15. To install it you'll need a clean |miniconda| environment. Install Miniconda and activate base.

**1a: Installation of Savu-lite from savu-dep conda channel**

*Usually the easiest method which will install Savu-lite into a new Savu environment.*

1. >>> conda create -n savu
2. >>> conda activate savu
3. >>> conda install savu-lite -c conda-forge -c savu-dep -c ccpi -c astra-toolbox/label/dev

**1b: Installation of Savu-lite using the explicit list of packages**

*This method requires cloning the repository and then installing all the dependencies from the explicit list file.*
*After all dependencies installed, Savu-lite is installed into the existing environment. Although more hassle, this is the fastest method and also recommended for the developer.*

1. >>> git clone https://github.com/DiamondLightSource/Savu.git
2. Move to Savu directory
3. >>> conda create --yes --name savu --file install/savu_lite37/spec-savu_lite_latest.txt
4. >>> python setup.py install

Savu-lite will be installed in conda environment in Miniconda folder. 
