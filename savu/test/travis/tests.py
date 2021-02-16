import os, pathlib
import sys
from pytest import main

savuPath = os.path.dirname(os.path.realpath(__file__))
os.chdir( savuPath )
# the tests will use the command line version of pytest.main() run
# the parallel multicore run requires pytest-xdist software
try:
    sys.exit(main(["-n", "4"]))
except:
    print("No pytest-xdist module (parallel), running serial")
    sys.exit(main())
