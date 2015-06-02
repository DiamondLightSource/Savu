Savu User Guide
***************

The easiest way to get Savu running is to use the Anaconda Python
distribution, if you don't have this already, please download it 
from http://continuum.io/downloads.

put the .sh file into the install directory and then run

    >>> bash Anaconda-2.2.0-Linux-x86_64.sh

you will need to update this a little with the following things
    
    pip install mpi4py

Once you have installed this, now get the code from github

    >>> git clone https://github.com/DiamondLightSource/Savu.git

you should probably keep a record of the place where this is

    >>> export SAVU_HOME=/path/to/Savu

Now you can add the new Savu repository to the Python Path

    >>> export PYTHONPATH=$PYTHONPATH:$SAVU_HOME

now you should be able to run up your python interpreter, and call

    >>> import savu
    >>> savu.run_tests()

running the tests simply makes sure that everything is OK.  Watch out for
failures as this will highlight if there are any modules which you should
inlcude, for example the astra toolbox if you want to use it.

Running the pipeline
********************

So now you can use the standard runners to launch a savu pipleine

    >>> python $SAVU_HOME/savu/tomo_recon.py --help
    Usage: tomo_recon.py [options] input_file output_directory
    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit
      -n NAMES, --names=NAMES
                            Process names
      -f PROCESS_FILENAME, --filename=PROCESS_FILENAME
                            The filename of the process file
      -l, --log2db          Set logging to go to a database

Key to this is that the files are correct, the input file needs to be
of a supported file.  For example a file compatable with NXtomo (as found
at Diamond Light Source)

You will also need a process file, this file contains the list of plugins
which will be run to process the file.  This can be generated using the 
config generator found in the scripts directory of 

    >>> python $SAVU_HOME/scripts/config_generator/savu_config.py

