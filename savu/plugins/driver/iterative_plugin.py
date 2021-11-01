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
.. module:: iterative_plugin
   :platform: Unix
   :synopsis: Driver for iterative plugins

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.driver.plugin_driver import PluginDriver


class IterativePlugin(PluginDriver):
    """
    Allows the plugin to be repeated, keeping the parameters from the previous
    iteration.
    """

    def __init__(self):
        super(IterativePlugin, self).__init__()
        self._ip_iteration = 0
        self._ip_fixed_iterations = False
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
        self._ip_pattern_dict = {}
        self._ip_data_dict['iterating'] = {}
        self._ip_pattern_dict['iterating'] = {}

    def _run_plugin(self, exp, transport):
        """ Runs the pre_process, process and post_process methods.
        """
        self.__set_original_datasets()

        while not self._ip_complete:
            print ("Iteration", self._ip_iteration, "...")
            self.__set_datasets()  # change the pattern in this function?
            self._run_plugin_instances(transport, self.get_communicator())
            if transport.no_processing:
                self.set_processing_complete()
            if self._ip_fixed_iterations and \
                    self._ip_iteration == self._ip_fixed_iterations-1:
                self.set_processing_complete()
            self._ip_iteration += 1
        self.__finalise_datasets()

    def __set_datasets(self):
        '''
        Set the input and output datasets such that
        - the output dataset from the previous iteration is the input dataset of
          the current iteration that is about to be performed
        - the input dataset from the previous iteration is used to write the
          output of the urrent iteration that is about to be performed
        '''
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

#    def __set_patterns(self):
#        # The pattern dict key
#        # pattern_dict can be:
#        # dict[int=itr] = [list of string patterns]
#        # dict[int=itr] = {dictionary of <dataset, pattern> key value pairs}
#        # dict['iterating'] = [list of string patterns]
#        # dict['iterating'] = {dictionary of <dataset, pattern> key value pairs}
#        params = self.parameters
#        if self._ip_iteration in self._ip_pattern_dict.keys():
#            # initial attempt at recalculating every time
#            params['in_datasets'] =


    def get_iteration(self):
        return self._ip_iteration

    def __finalise_datasets(self):
        '''
        Inspect the two Data objects that are used to contain the input and
        output data for iterations over the course of the iterative processing
        (input/output depending on which particular iteration was being done).

        Mark one of them as the "final dataset" to be added to the output
        NeXuS file, and mark the other as "to be removed".

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

    def set_processing_complete(self):
        self._ip_complete = True

    def set_iterations(self, nIterations):
        if isinstance(nIterations, int):
            self._ip_fixed_iterations = nIterations
        else:
            raise Exception('nIterations should be an integer.')

    def set_iteration_datasets(self, itr, in_data, out_data, pattern=None):
        self._ip_data_dict[itr] = [in_data, out_data]
        self._ip_pattern_dict[itr] = pattern

    def create_clone(self, clone, data):
        clone.create_dataset(data)
        clone.data_info.set('clone', data.get_name())
        # alternate a dataset with its clone
        self.set_alternating_datasets(data, clone)

    def set_alternating_datasets(self, d1, d2):
        names = [d1.get_name(), d2.get_name()]
        if not any([True if 'itr_clone' in i else False for i in names]):
            raise Exception('Alternating datasets must contain a clone.  These'
                            ' are found at the end of the out_datasets list')
        self._ip_data_dict['iterating'][d1] = d2

    def set_alternating_patterns(self, patterns):
        if isinstance(patterns, list):
            self._ip_pattern_dict['iterating'] = patterns
        elif isinstance(patterns, dict):
            for data, plist in patterns:
                self._ip_pattern_dict['iterating'][data] = plist
        else:
            raise Exception("Please pass the patterns as a list or a dict.")

    def get_alternating_datasets(self):
        return self._ip_data_dict['iterating']

    def __set_original_datasets(self):
        self.in_data = self.parameters['in_datasets']
        self.out_data = self.parameters['out_datasets']

    def get_original_datasets(self):
        return self.in_data, self.out_data
