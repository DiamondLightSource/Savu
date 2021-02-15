import os, pathlib
#import pytest
import re
import sys
from pytest import main

savuPath = os.path.dirname(os.path.realpath(__file__))
os.chdir( savuPath )

#if __name__ == '__main__':
#sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
#
sys.exit(main(["-n", "4"]))
"""
exitcode = pytest.main()
print(exitcode)
if (exitcode == "ExitCode.TESTS_FAILED"):
    print("NOW NOW")
    exit(1)
else:
    exit(0)
"""
#pytest.main()
#pytest.main(["-n", "mytestdir"])
