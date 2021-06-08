
"""
.. module:: plugin_doc_test_runner
   :platform: Unix
   :synopsis: unittest test for plugin restructured text file documentation
.. moduleauthor: Jessica Verschoyle

"""
import os
import unittest

def load_tests(loader, tests, pattern):
    """Discover and load all unit tests in all files named ``*_test.py`` in
    `doc_tests/plugins/``
    """

    # determine Savu base path
    savu_base_path = \
        os.path.dirname(os.path.realpath(__file__)).split('savu')[0]

    start_dir = savu_base_path + "savu/test/travis/doc_tests/plugins/"
    loader = unittest.TestLoader()
    test_suite = loader.discover(start_dir, pattern="*_test.py")
    return test_suite


if __name__ == "__main__":
    unittest.main()
