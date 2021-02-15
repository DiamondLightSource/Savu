import os, pathlib
import pytest

savuPath = os.path.dirname(os.path.realpath(__file__))

#os.chdir( savuPath  + '/framework_tests' )
#pytest.main()
#os.chdir( savuPath + '/plugin_tests' )
#pytest.main()
#os.chdir( savuPath + '/process_list_tests' )
os.chdir( savuPath )
pytest.main()
