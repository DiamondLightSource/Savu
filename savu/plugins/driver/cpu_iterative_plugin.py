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
.. module:: cpu_iterative_plugin
   :platform: Unix
   :synopsis: Base class for all plugins which use a CPU on the target machine
   and have the ability to be iterative

.. moduleauthor:: Daniil Kazantsev & Yousef Moazzam <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.driver.plugin_driver import PluginDriver
from savu.plugins.driver.basic_driver import BasicDriver

import os
_base = BasicDriver if os.environ['savu_mode'] == 'basic' else PluginDriver


class CpuIterativePlugin(_base):

    def __init__(self):
        super(CpuIterativePlugin, self).__init__()
        # set any plugin that inherits from CpuIterativePluign to be iterative
        self._is_iterative = True
        # the current iteration: starts counting at 0 (zero-based)
        self._ip_iteration = 0
        # the number of iterations to perform: starts counting at 1 (one-based)
        # TODO: should this have a starting/default value of 1 rather than
        #  False, to signify that the default number of iterations is just 1?
        # self._ip_fixed_iterations = False
        self._ip_fixed_iterations = 3
        # a bool describing if all iterations have been completed
        self._ip_complete = False
        # The _ip_data_dict value eventually holds 3 keys:
        # - 'iterating'
        # - 0
        # - 1
        # The name of the 0 key refers to the 0th iteration, and the name of the
        # 1 key refers to the 1st iteration
        # The values of the 0 key is a list containing two lists (both with only
        # one element in them):
        # - a list contining the input NeXuS file
        # - a list containing the Data object used as an input AND output dataset
        # (depending on the iteration number) with the "original" backing file
        # (ie, NOT the "cloned" backing file)
        # The value of the 1 key is a list containing two lists (one containing
        # one element, one containing two elements):
        # - a list containing the input NeXuS file, and also the Data object
        #   with the "original" backing file
        # - a list containing the Data object with the "clone" backing file
        self._ip_data_dict = {}
        # The dict value of the 'iterating' key contains only one key-value
        # pair throughout all iterations:
        # - the key is the "original" Data object
        # - the value is the "cloned" Data object
        # TODO: figure out how the name of the backing files created is set (ie,
        #  where does the "iterative_ccpi_denoising" bit come from?)
        self._ip_data_dict['iterating'] = {}

        # similar to _ip_data_dict, but for the pattern of the original &
        # cloned datasets, depending on the current iteration number
        self._ip_pattern_dict = {}
        self._ip_pattern_dict['iterating'] = {}

    def setup_iterative_plugin(self):
        '''
        Run this method instead of the setup() method in the plugin, if the
        plugin is being run iteratively.

        Setup the cloned datasets only if the number of iterations is
        greater than 1 (so then the cloned dataset isn't unnecessarily defined
        for running just a single iteration).
        '''
        if self._ip_fixed_iterations and self._ip_fixed_iterations > 1:
            self.__set_original_datasets()
            # get the in and out datasets, like in IterativeCcpiDenosing.setup()
            in_dataset, out_dataset = self.get_original_datasets()

            # get the PluginData objcts, like in IterativeCcpiDenosing.setup()
            in_pData = self.parameters['plugin_in_datasets']
            out_pData = self.parameters['plugin_out_datasets']

            # set the pattern for the single input dataset
            in_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')

            # Cloned datasets are at the end of the out_dataset list
            out_dataset[0].create_dataset(in_dataset[0])

            # What is a cloned dataset?
            # Since each dataset in Savu has its own backing hdf5 file, a dataset
            # cannot be used for input and output at the same time.  So, in the
            # case of iterative plugins, if a dataset is used as output and then
            # as input on the next iteration, the subsequent output must be a
            # different file.
            # A cloned dataset is a copy of another dataset but with a different
            # backing file.  It doesn't have a name, is not accessible as a dataset
            # in the framework and is only used in alternation with another
            # dataset to allow it to be used as both input and output
            # simultaneously.

            # This is a cloned dataset (of out_dataset[0])
            self.create_clone(out_dataset[1], out_dataset[0])

            # set the pattern for the PluginData objects associated with the two
            # ouptut datasets (original and clone)
            out_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')
            out_pData[1].plugin_data_setup(self.parameters['pattern'], 'single')

            # set the input and output datasets for the first iteration
            self.set_iteration_datasets(0, [in_dataset[0]], [out_dataset[0]],
                                        self.parameters['pattern'])
            # set the input and output datasets for subsequent iterations
            self.set_iteration_datasets(1, [in_dataset[0], out_dataset[0]],
                                        [out_dataset[1]],
                                        self.parameters['pattern'])
            # out_dataset[0] and out_dataset[1] will continue to alternate for
            # all remaining iterations i.e. output becomes input and input becomes
            # output.

    def _run_plugin(self, exp, transport):
        '''
        Execute the iterative processing.
        '''
        # The docstring of this method in IterativePlugin is the following:
        #
        # Run the pre_process, process, and post_process methods.
        #
        # However, there is no obvious point where those methods are called,
        # so perhaps this docstring isn't quite accurate? (Also note that this
        # sentence has been copied from the docstring
        # BaseDriver._run_plugin_instances(), so maybe it is just a generic
        # description of what this method SHOULD do, but doesn't yet do,
        # in IterativePlugin)

        if self._ip_complete:
            self.__finalise_datasets()
            return
        else:
            print(f"Iteration {self._ip_iteration}...")
            self.__set_datasets()
            self._run_plugin_instances(transport, self.get_communicator())
            # transport.no_processing is related to the nTrans variable that
            # is seen in various places in the "transport layer"
            # TODO: figure out what nTrans is/means
            if transport.no_processing:
                self.set_processing_complete()

            # if self._ip_fixed_iterations has been set to something other
            # than its original value of False, and if the current iteration
            # (the one that has just been completed) is the LAST iteration,
            # then processing has been completed
            #
            # Note that _ip_iteration starts counting at 0,
            # but _ip_fixed_iterations starts counting at 1, so if you have
            # reached _ip_iteration=n, then this means that n+1 iterations
            # have been performed
            if self._ip_fixed_iterations and \
                    self._ip_iteration == self._ip_fixed_iterations - 1:
                self.set_processing_complete()
            self._ip_iteration += 1
            # start another iteration
            self._run_plugin(exp, transport)

    def create_clone(self, clone, data):
        clone.create_dataset(data)
        clone.data_info.set('clone', data.get_name())
        # alternate a dataset with its clone
        self.set_alternating_datasets(data, clone)

    def __set_datasets(self):
        '''
        Set the input and output datasets such that
        - the output dataset from the previous iteration is the input dataset of
          the current iteration that is about to be performed
        - the input dataset from the previous iteration is used to write the
          output of the current iteration that is about to be performed
        '''
        # TODO: perhaps the pattern should be changed here, to make use of
        #  the same logic that is being used to switch the original & cloned
        #  data?
        params = self.parameters
        # Only the 0th and 1st iterations are set in _ip_data_dicts, there is
        # NOT a key for every iteration in _ip_data_dict, hence this if/elif
        # block
        if self._ip_iteration in list(self._ip_data_dict.keys()):
            # If on the 0th or 1st iteration, set the in_datasets and
            # out_datasets according to the structure  defined in _ip_data_dict
            #
            # The body of this if statement is essentially a way to "set up" the
            # input and ouput datasets so that for iterations after the 0th and
            # 1st, the two datasets that are swapped between being used for
            # input or output (depending on the particular iteration) can be
            # swapped WITHOUT having to define a key-value pair in
            # _ip_data_dict for EVERY SINGLE ITERATION
            params['in_datasets'] = self._ip_data_dict[self._ip_iteration][0]
            params['out_datasets'] = self._ip_data_dict[self._ip_iteration][1]
        elif self._ip_iteration > 0:
            # If on an iteration greater than 1 (since the if statement catches
            # both iteration 0 and 1), then there is some (fiddly...) logic
            # here to essentially SWAP the out dataset from the previous
            # iteration with the in dataset of the previous iteration
            #
            # Practically speaking, this means that:
            # - the out dataset from the previous iteration is used as the input
            #   for the current iteration that is about to be performed
            # - the in dataset from the previous iteration is free to be used to
            #   write the output of the current iteration that is about to be
            #   performed
            p = [params['in_datasets'], params['out_datasets']]
            for s1, s2 in self._ip_data_dict['iterating'].items():
                a = [0, p[0].index(s1)] if s1 in p[0] else [1, p[1].index(s1)]
                b = [0, p[0].index(s2)] if s2 in p[0] else [1, p[1].index(s2)]
                p[a[0]][a[1]], p[b[0]][b[1]] = p[b[0]][b[1]], p[a[0]][a[1]]

    def set_alternating_datasets(self, d1, d2):
        names = [d1.get_name(), d2.get_name()]
        if not any([True if 'itr_clone' in i else False for i in names]):
            raise Exception('Alternating datasets must contain a clone.  These'
                            ' are found at the end of the out_datasets list')
        self._ip_data_dict['iterating'][d1] = d2

    def get_alternating_datasets(self):
        return self._ip_data_dict['iterating']

    def set_iteration_datasets(self, itr, in_data, out_data, pattern=None):
        self._ip_data_dict[itr] = [in_data, out_data]
        self._ip_pattern_dict[itr] = pattern

    def set_processing_complete(self):
        '''
        Signal that the final iteration has been executed.
        '''
        self._ip_complete = True

    def __finalise_datasets(self):
        '''
        Inspect the two Data objects that are used to contain the input and
        output data for iterations over the course of the iterative processing
        (input/output depending on which particular iteration was being done).

        Mark one of them as the "final dataset" to be added to the output
        NeXuS file, and mark the other as "obsolete/to be removed".

        The decision between which one is kept and which one is removed
        depends on which Data object contains the OUTPUT of the very last
        iteration.

        For an odd number of iterations, this is the "original" Data object.
        For an even number of iteration, this is the "clone" Data object.
        '''
        for s1, s2 in self._ip_data_dict['iterating'].items():
            name = s1.get_name()
            name = name if 'itr_clone' not in name else s2.get_name()
            final_dataset = s1 if s1 in self.parameters['out_datasets'] else s2
            obsolete = s1 if s1 is not final_dataset else s2
            obsolete.remove = True

            # switch names if necessary
            if final_dataset.get_name() != name:
                # If this is true, then the output dataset of the last
                # iteration is the clone Data object (hence, the mismatched
                # names).
                #
                # So then:
                # - obsolete = original
                # - final_dataset = clone
                #
                # which means that the CLONED dataset needs to be set in the
                # Experiment object (self.exp) as the "out data", but under
                # the name of the ORIGINAL dataset.
                # And also, the ORIGINAL dataset is set in the Experiment
                # object, but under the name of the CLONED/OBSOLETE dataset
                temp = obsolete
                self.exp.index['out_data'][name] = final_dataset
                self.exp.index['out_data'][s2.get_name()] = temp
                # One last thing to do in this case is to set the "name"
                # inside the Data object that final_result is set to.
                #
                # This is because, in this case, the CLONED dataset is in
                # final_result, and the "name" within the Data object will
                # be some value like "itr_0".
                #
                # However, the name within the Data object needs to be the
                # name of the ORIGINAL Data object in order for the creation
                # of the output NeXuS file to work.
                final_dataset._set_name(name)

    def __set_original_datasets(self):
        '''
        Utility function to make the (original) in dataset, and out dataset,
        easier to reference
        '''
        self.in_data = self.parameters['in_datasets']
        self.out_data = self.parameters['out_datasets']

    def get_original_datasets(self):
        '''
        Helper function to get the in and out datasets more easily.
        '''
        return self.in_data, self.out_data