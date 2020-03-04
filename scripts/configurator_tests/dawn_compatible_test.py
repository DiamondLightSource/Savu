'''
This tests the functions required by dawn. If these tests break, the dawn \
integration will certainly fail.
'''

import unittest
import scripts.config_generator.config_utils as cu
import savu.plugins.utils as pu
from savu.plugins.utils import dawn_plugins


class DawnCompatibleTest(unittest.TestCase):
    def test_populate_plugins(self):
        cu.populate_plugins()

    def test_dawn_plugins_found(self):
        cu.populate_plugins()
        self.assertGreater(len(pu.dawn_plugins), 0)

    def test_dawn_plugin_params_found(self):
        cu.populate_plugins(dawn=True)
        self.assertTrue(
            isinstance(pu.dawn_plugin_params[list(pu.dawn_plugins.keys())[0]],
                       dict))

    def test_load_plugin(self):
        cu.populate_plugins()
        plugin_path = pu.dawn_plugins[dawn_plugins.keys()[0]]['path2plugin']
        inst = pu.load_class(plugin_path)()
        sl = inst.__dict__['slice_list']
        exp = inst.__dict__['exp']


if __name__ == '__main__':
    unittest.main()
