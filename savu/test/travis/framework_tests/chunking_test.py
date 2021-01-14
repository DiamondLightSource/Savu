# Copyright 2014 Diamond Light Source Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. module:: chunking_tests
   :platform: Unix
   :synopsis: checking the chunking for a variety of pattern transforms

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import unittest
from savu.test import test_utils as tu
import numpy as np

from savu.data.chunking import Chunking
from savu.data.experiment_collection import Experiment


class ChunkingTests(unittest.TestCase):
    def create_chunking_instance(self, current_list, nnext_list, nProcs):
        current = self.create_pattern('a', current_list)
        nnext = self.create_pattern('b', nnext_list)
        options = tu.set_experiment('tomoRaw')
        options['processes'] = list(range(nProcs))
        # set a dummy process list
        options['process_file'] = \
            tu.get_test_process_path('loaders/basic_tomo_process.nxs')
        exp = Experiment(options)
        test_dict = {'current': current, 'next': nnext}
        chunking = Chunking(exp, test_dict)
        return chunking

    def create_pattern(self, name, pattern_list):
        pattern = {name: {'max_frames_transfer': pattern_list[0],
                          'slice_dims': pattern_list[1],
                          'core_dims': pattern_list[2]}}
        return pattern

    def get_nChunks(self, shape, chunks):
        prod = 1
        for i in range(len(shape)):
            prod *= np.ceil(shape[i]/float(chunks[i]))
        return prod

    def amend_chunks(self, chunks):
        """ If any temporary amendments are applied to the final chunking
        values in the framework, then remove these here. """
        return chunks

    def test_chunks_3D_1(self):
        current = [1, (0,), (1, 2)]
        nnext = [1, (0,), (1, 2)]
        shape = (5000, 500, 500)
        nProcs = 1
        chunking = self.create_chunking_instance(current, nnext, nProcs)
        chunks = chunking._calculate_chunking(shape, np.float32)
        self.assertEqual(self.amend_chunks(chunks), (1, 500, 500))

        nProcs = 2
        chunking = self.create_chunking_instance(current, nnext, nProcs)
        chunks = chunking._calculate_chunking(shape, np.float32)
        self.assertEqual(self.amend_chunks(chunks), (1, 500, 500))

        shape = (5000, 5000, 5000)
        chunking = self.create_chunking_instance(current, nnext, nProcs)
        chunks = chunking._calculate_chunking(shape, np.float32)
        self.assertEqual(self.amend_chunks(chunks), (1, 625, 313))

        shape = (5000, 5000, 5000)
        chunking = self.create_chunking_instance(current, nnext, nProcs)
        chunks = chunking._calculate_chunking(shape, np.float32)
        self.assertEqual(self.amend_chunks(chunks), (1, 625, 313))

        shape = (1, 800, 500)
        chunking = self.create_chunking_instance(current, nnext, nProcs)
        chunks = chunking._calculate_chunking(shape, np.float32)
        self.assertEqual(self.amend_chunks(chunks), (1, 400, 500))

    def test_chunks_3D_2(self):
        current = [1, (0,), (1, 2)]
        nnext = [1, (1,), (0, 2)]
        shape = (50, 300, 100)
        nProcs = 1
        chunking = self.create_chunking_instance(current, nnext, nProcs)
        chunks = chunking._calculate_chunking(shape, np.float32)
        self.assertEqual(self.amend_chunks(chunks), (50, 50, 100))

        current = [8, (0,), (1, 2)]
        nnext = [4, (1,), (0, 2)]
        chunking = self.create_chunking_instance(current, nnext, nProcs)
        chunks = chunking._calculate_chunking(shape, np.float32)
        self.assertEqual(self.amend_chunks(chunks), (48, 52, 100))

        nProcs = 10
        chunking = self.create_chunking_instance(current, nnext, nProcs)
        chunks = chunking._calculate_chunking(shape, np.float32)
        self.assertEqual(self.amend_chunks(chunks), (8, 28, 100))

    def test_chunks_4D_1(self):
        current = [1, (0, 1), (2, 3)]
        nnext = [1, (0, 1), (2, 3)]
        shape = (800, 700, 600, 500)
        nProcs = 1
        chunking = self.create_chunking_instance(current, nnext, nProcs)
        chunks = chunking._calculate_chunking(shape, np.float32)
        self.assertEqual(self.amend_chunks(chunks), (1, 1, 300, 500))

        current = [1, (0, 1), (2, 3)]
        nnext = [1, (2, 3), (0, 1)]
        chunking = self.create_chunking_instance(current, nnext, nProcs)
        chunks = chunking._calculate_chunking(shape, np.float32)
        self.assertEqual(self.amend_chunks(chunks), (23, 22, 22, 22))

        current = [1, (0,), (1, 2, 3)]
        nnext = [1, (0,), (1, 2, 3)]
        chunking = self.create_chunking_instance(current, nnext, nProcs)
        chunks = chunking._calculate_chunking(shape, np.float32)
        self.assertEqual(self.amend_chunks(chunks), (1, 44, 75, 63))

        current = [4, (0,), (1, 2, 3)]
        nnext = [8, (1, 2), (0, 3)]
        chunking = self.create_chunking_instance(current, nnext, nProcs)
        chunks = chunking._calculate_chunking(shape, np.float32)
        self.assertEqual(self.amend_chunks(chunks), (8, 8, 7, 500))

        nProcs = 200
        current = [4, (0,), (1, 2, 3)]
        nnext = [8, (1, 2), (0, 3)]
        chunking = self.create_chunking_instance(current, nnext, nProcs)
        chunks = chunking._calculate_chunking(shape, np.float32)
        self.assertEqual(self.amend_chunks(chunks), (4, 8, 8, 500))


if __name__ == "__main__":
    unittest.main()
