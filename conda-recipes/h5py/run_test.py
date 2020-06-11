import os

os.environ['OMPI_MCA_plm'] = 'isolated'
os.environ['OMPI_MCA_btl_vader_single_copy_mechanism'] = 'none'
os.environ['OMPI_MCA_rmaps_base_oversubscribe'] = 'yes'

import h5py
import h5py._conv
import h5py._errors
import h5py._objects
import h5py._proxy
import h5py.defs
import h5py.h5
import h5py.h5a
import h5py.h5d
import h5py.h5f
import h5py.h5fd
import h5py.h5g
import h5py.h5i
import h5py.h5l
import h5py.h5o
import h5py.h5p
import h5py.h5r
import h5py.h5s
import h5py.h5t
import h5py.h5z
import h5py.utils

have_mpi = h5py.get_config().mpi
should_have_mpi = True
assert have_mpi == should_have_mpi, "Expected mpi=%r, got %r" % (should_have_mpi, have_mpi)

# skip TestDrivers.test_mpio
import h5py.tests.old.test_file
delattr(h5py.tests.old.test_file.TestDrivers, 'test_mpio')

from sys import exit
exit(0) if h5py.run_tests().wasSuccessful() else exit(1)
