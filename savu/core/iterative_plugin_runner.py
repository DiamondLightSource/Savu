from savu.core.iterate_plugin_group_utils import shift_plugin_index


class IteratePluginGroup():
    '''
    Class for iterating a set/group of plugins in a process list
    '''

    def __init__(self, plugin_runner, start_index, end_index, iterations):
        self.in_data = None
        self.out_data = None
        # PluginRunner object for running the individual plugns in the group of
        # pluigns to iterate over
        self.plugin_runner = plugin_runner

        # nPlugin index of plugin that is at the start of group to iterate over
        self.start_index = start_index
        # nPlugin index of plugin that is at the end of group to iterate over
        self.end_index = end_index

        # dict of plugins needed to run the plugins using
        # PluginRunner.__run_plugin()
        self.plugins = []

        # Note: copied from CpuIterativePlugin

        # the current iteration: starts counting at 0 (zero-based)
        self._ip_iteration = 0
        # the number of iterations to perform: starts counting at 1 (one-based)
        self._ip_fixed_iterations = iterations
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
        self._ip_data_dict['iterating'] = {}

        # similar to _ip_data_dict, but for the pattern of the original &
        # cloned datasets, depending on the current iteration number
        self._ip_pattern_dict = {}
        self._ip_pattern_dict['iterating'] = {}

    def setup_datasets(self):
        '''
        Setup the cloned datasets in the start and end plugins in the group to
        iterate over
        '''
        self.__set_original_datasets()
        # get the in and out datasets, like in IterativeCcpiDenosing.setup()
        in_dataset, out_dataset = self.get_original_datasets()

        # set the input and output datasets for the first iteration
        self.set_iteration_datasets(0, [in_dataset[0]], [out_dataset[0]],
                                    self.start_plugin.parameters['pattern'])
        # set the input and output datasets for subsequent iterations
        self.set_iteration_datasets(1, [in_dataset[0], out_dataset[0]],
                                    [out_dataset[1]],
                                    self.end_plugin.parameters['pattern'])
        # out_dataset[0] and out_dataset[1] will continue to alternate for
        # all remaining iterations i.e. output becomes input and input becomes
        # output.

    def _execute_iteration_0(self, exp, transport):
        '''
        Run plugins for iteration 0
        '''
        start = shift_plugin_index(exp, self.start_index)
        end = shift_plugin_index(exp, self.end_index)

        nPlugin = exp.meta_data.get('nPlugin')
        exp_coll = exp._get_collection()
        if start == end and nPlugin == end:
            # start == end -> group of plugins to iterate over is a single
            # plugin

            plugin_name = \
                self.plugin_runner._PluginRunner__run_plugin(
                    exp_coll['plugin_dict'][nPlugin],
                    clean_up_plugin=False)

            # since the end plugin has now been run, the group of plugins to
            # iterate over has been executed once, and this counts as having
            # done one iteration (ie, at this point, iteration 0 is
            # complete)
            self.increment_ip_iteration()
            # kick off all subsequent iterations
            self._execute_iterations(exp, transport)
            # finished all iterations, set which output dataset to keep, and
            # which to remove
            self._finalise_iterated_datasets()
        else:
            # start != end -> group of plugins to iterate over is more than one
            # plugin
            if nPlugin == start:
                # start plugin is being run, on iteration 0
                print(f"Iteration {self._ip_iteration}")
                plugin = self.plugin_runner._PluginRunner__run_plugin(
                    exp_coll['plugin_dict'][nPlugin],
                    clean_up_plugin=False)
                plugin_name = plugin.name
                self.set_start_plugin(plugin)
            elif nPlugin == end:
                # end plugin is being run, on iteration 0

                plugin_name = \
                    self.plugin_runner._PluginRunner__run_plugin(
                        exp_coll['plugin_dict'][nPlugin],
                        clean_up_plugin=False)

                # since the end plugin has now been run, the group of plugins to
                # iterate over has been executed once, and this counts as having
                # done one iteration (ie, at this point, iteration 0 is
                # complete)
                self.increment_ip_iteration()
                # kick off all subsequent iterations
                self._execute_iterations(exp, transport)
                # finished all iterations, set which output dataset to keep, and
                # which to remove
                self._finalise_iterated_datasets()
            elif nPlugin >= start and nPlugin <= end:
                # a "middle" plugin is being run on iteration 0
                plugin = self.plugin_runner._PluginRunner__run_plugin(
                    exp_coll['plugin_dict'][nPlugin])
                plugin_name = plugin.name
            else:
                info_dict = {
                    'start_index': self.start_index,
                    'end_index': self.end_index
                }
                err_str = f"Encountered an unknown case when running inside " \
                    f"an iterative loop. IteratePluginGroup info: {info_dict}"
                raise Exception(err_str)

        return plugin_name

    def _execute_iterations(self, exp, transport):
        '''
        Execute all iterations from iteration 1 onwards (iteration 0 is
        currently handled by methods in PluginRunner).
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

        while self._ip_iteration < self._ip_fixed_iterations:
            print(f"Iteration {self._ip_iteration}...")
            self.__set_datasets()
            # replace this with the PluginRunner.__run_plugin() method to run
            # the individual plugins in the group of plugins to iterate
            #self._run_plugin_instances(transport, self.get_communicator())

            # clean up the plugins in the group to iterate over IF the last
            # iteration is being executed
            if self._ip_iteration == self._ip_fixed_iterations - 1:
                clean_up_plugin = True
            else:
                clean_up_plugin = False
            # naughty naughty, to run a double underscore method, but for now,
            # just testing...
            for plugin in self.plugins:
                print(f"Running {plugin.name} in iterative group of plugins")
                # TODO: need to pass the plguin dict, or something more than an
                # empty dict...
                self.plugin_runner._PluginRunner__run_plugin({},
                    clean_up_plugin=clean_up_plugin,
                    plugin=plugin)

            # if self._ip_fixed_iterations has been set to something other
            # than its original value of False, and if the current iteration
            # (the one that has just been completed) is the LAST iteration,
            # then processing has been completed
            #
            # Note that _ip_iteration starts counting at 0,
            # but _ip_fixed_iterations starts counting at 1, so if you have
            # reached _ip_iteration=n, then this means that n+1 iterations
            # have been performed
            self.increment_ip_iteration()

    def increment_ip_iteration(self):
        self._ip_iteration += 1

    def __set_original_datasets(self):
        '''
        Utility function to make the (original) in dataset, and out dataset,
        easier to reference
        '''
        self.in_data = self.start_plugin.parameters['in_datasets']
        self.out_data = self.end_plugin.parameters['out_datasets']

    def get_original_datasets(self):
        '''
        Helper function to get the in and out datasets more easily.
        '''
        return self.in_data, self.out_data

    def get_plugin_datasets(self):
        '''
        Helper function to get the in and out plugin datasets more easily.
        '''
        return self.start_plugin.parameters['plugin_in_datasets'], \
            self.end_plugin.parameters['plugin_out_datasets']

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

    def set_iteration_datasets(self, itr, in_data, out_data, pattern=None):
        self._ip_data_dict[itr] = [in_data, out_data]
        self._ip_pattern_dict[itr] = pattern

    def set_start_plugin(self, plugin):
        '''
        Set the plugin that is at the start of the group to iterate over
        '''
        self.start_plugin = plugin

    def set_end_plugin(self, plugin):
        '''
        Set the plugin that is at the end of the group to iterate over
        '''
        self.end_plugin = plugin

    def add_plugin_to_iterate_group(self, plugin):
        '''
        Append plugin dict to list fo plguins that are part of the group to
        iterate over
        '''
        self.plugins.append(plugin)

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
            self.start_plugin.parameters['in_datasets'] = [self._ip_data_dict[self._ip_iteration][0][-1]]
            self.end_plugin.parameters['out_datasets'] = self._ip_data_dict[self._ip_iteration][1]
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
            p = [
                self.start_plugin.parameters['in_datasets'],
                self.end_plugin.parameters['out_datasets']
            ]

            for s1, s2 in self._ip_data_dict['iterating'].items():
                a = [0, p[0].index(s1)] if s1 in p[0] else [1, p[1].index(s1)]
                b = [0, p[0].index(s2)] if s2 in p[0] else [1, p[1].index(s2)]
                p[a[0]][a[1]], p[b[0]][b[1]] = p[b[0]][b[1]], p[a[0]][a[1]]

    def _finalise_iterated_datasets(self):
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
            final_dataset = s1 if s1 in self.end_plugin.parameters['out_datasets'] else s2
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

    def set_alternating_datasets(self):
        d1 = self.end_plugin.parameters['out_datasets'][0]
        d2 = self.end_plugin.parameters['out_datasets'][1]
        names = [d1.get_name(), d2.get_name()]
        if not any([True if 'itr_clone' in i else False for i in names]):
            raise Exception('Alternating datasets must contain a clone.  These'
                            ' are found at the end of the out_datasets list')
        self._ip_data_dict['iterating'][d1] = d2