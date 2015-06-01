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


