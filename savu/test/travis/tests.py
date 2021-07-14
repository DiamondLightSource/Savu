import os, pathlib
import sys
from pytest import main

savuPath = os.path.dirname(os.path.realpath(__file__))
os.chdir( savuPath )
# the tests will use the command line version of pytest.main() run
# the parallel multicore run requires pytest-xdist software
sys.exit(main(["-n", "auto", "-v"]))
