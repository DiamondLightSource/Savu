import os
import fnmatch
from scripts.config_generator.content import Content

def get_all_files_from(folder):
    all_files = []
    for root, dirs, files in os.walk(folder, topdown=True):
        files = [os.path.join(root[root.index(folder)+1+len(folder):], file) for file in files]
        all_files.extend(files)
    return all_files


def get_test_process_list(folder):
    test_process_list = []
    for root, dirs, files in os.walk(folder, topdown=True):
        files[:] = [fi for fi in files if fi.split('.')[-1] == 'nxs']
        # since there are some nxs files inside the subfolders we attach the subfolder
        # name to nxs without the root folder
        files = [os.path.join(root[root.index(folder)+1+len(folder):], file) for file in files]
        test_process_list.extend(files)
    return test_process_list


def get_process_list(folder, search=False):
    process_list = []
    plugin_list = []
    exclude_dir = ['__pycache__']
    exclude_file = ['__init__.py']
    for root, dirs, files in os.walk(folder, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude_dir]
        files[:] = [fi for fi in files if fi.split('.')[-1] == 'py']
        files[:] = [fi for fi in files if fi not in exclude_file]
        processes = get_process_list_in_file(root, files)
        plugins = get_no_process_list_tests(root, files)
        for p in processes:
            process_list.append(p)
        for p in plugins:
            plugin_list.append(p)
    return process_list, plugin_list


def get_process_list_in_file(root, files):
    processes = []
    for fname in files:
        fname = root + '/' + fname
        in_file = open(fname, 'r')
        for line in in_file:
            if '.nxs' in line:
                processes.append(get_nxs_file_name(line))
        in_file.close()
    return processes

def find_plugin_for_process_list(folder, proc_list):
    plugin_name = []
    for root, dirs, files in os.walk(folder):
        for name in files:
            fname = root + '/' + name
            fname_nohead = fname.rsplit('/',1)[1]
            fname_type = os.path.splitext(fname_nohead)[1]
            if (fname_type == '.py'):
                in_file = open(fname, 'r')
                for line in in_file:
                    if '.nxs' in line:
                        nxs_name = get_nxs_file_name(line)
                        if fnmatch.fnmatch(str(nxs_name), proc_list):
                            plugin_name = fname
                            break
                in_file.close()
    return plugin_name

def get_no_process_list_tests(root, files):
    processes = []
    for fname in files:
        fname = root + '/' + fname
        in_file = open(fname, 'r')
        func = 'run_protected_plugin_runner_no_process_list'
        exclude = ['def', 'search_str']
        pos = 1
        param = get_param_name(func, pos, in_file, exclude=exclude)
        if param:
            in_file.seek(0)
            plugin_id_list = get_param_value_from_file(param, in_file)
            for pid in plugin_id_list:
                plugin_name = pid.split('.')[-1].split("'")[0]
                processes.append(plugin_name + '.py')
        in_file.close()
    return processes

def get_nxs_file_name(line):
    split_list = line.split("'")
    for entry in split_list:
        if 'nxs' in entry:
            if (len(entry.split(' ')) == 1):
                return entry


def get_param_name(func, pos, in_file, exclude=[]):
    """ Find the name of an argument passed to a function.

    :param str func: function name
    :param int pos: function argument position
    :param file in_file: open file to search
    :keyword list[str] exclude: ignore lines containing these strings.
                                Defaults to [].
    :returns: name associated with function argument
    :rtype: str
    """
    search_str = 'run_protected_plugin_runner_no_process_list('
    ignore = ['def', 'search_str']
    val_str = None
    for line in in_file:
        if search_str in line:
            if not [i in line for i in ignore].count(True):
                if ')' not in line:
                    line += next(in_file)
                params = line.split('(')[1].split(')')[0]
                val_str = params.split(',')[1].strip()
    return val_str


def get_param_value_from_file(param, in_file):
    """ Find all values associated with a parameter name in a file.

    :param str param: parameter name to search for
    :param file in_file: open file to search
    :returns: value associated with param
    :rtype: list[str]
    """
    param_list = []
    for line in in_file:
        if param in line and line.split('=')[0].strip() == param:
            if "\\" in line:
                line += next(in_file)
                line = ''.join(line.split('\\'))
            value = line.split('=')[1].strip()
            param_list.append(value)
    return param_list


def refresh_process_file(path):
    content = Content()
    # open
    content.fopen(path, update=True)
    # refresh
    positions = content.get_positions()
    for pos_str in positions:
        content.refresh(pos_str)
    # save
    content.save(content.filename)


