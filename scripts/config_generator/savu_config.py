'''
Created on 21 May 2015

@author: ssg37927
'''

import os

from savu.data.process_data import ProcessList
from savu.plugins import utils as pu
import pkgutil
import savu


class Content(object):

    def __init__(self, filename):
        self.process_list = ProcessList()
        if os.path.exists(filename):
            print "Opening file %s" % (filename)
            self.process_list.populate_process_list(filename)

    def display(self):
        print self.process_list.get_string()

    def save(self, filename):
        self.process_list.save_list_to_file(filename)


def _help(content, arg):
    """Display the help information"""
    for key in commands.keys():
        print "%s : %s" % (key, commands[key].__doc__)
    return content


def _open(content, arg):
    """Opens or creates a new configuration file with the given filename"""
    return Content(arg)


def _disp(content, arg):
    """Displays the process in the current list"""
    content.display()
    return content


def _list(content, arg):
    """List the plugins which have been registered for use"""
    for key in pu.plugins.keys():
        print key
    return content


def _save(content, arg):
    """Save the current list to disk with the filename given"""
    content.save(arg)

commands = {'open': _open,
            'help': _help,
            'disp': _disp,
            'list': _list,
            'save': _save}

if __name__ == '__main__':
    print "Starting Savu Config tool"

    # load all the packages in the plugins directory to register classes
    for loader, module_name, is_pkg in pkgutil.walk_packages(savu.plugins.__path__):
        try:
            module = loader.find_module(module_name).load_module(module_name)
        except:
            pass

    # set up things
    input_string = "startup"
    content = Content("")

    while True:
        input_string = raw_input(">>> ").strip()
        print "command is '%s'" % (input_string)

        command = input_string.split()[0]
        arg = ' '.join(input_string.split()[1:])

        if 'exit' in command:
            break

        # try to run the command
        if command in commands.keys():
            content = commands[command](content, arg)
        else:
            print "I'm sorry, thats not a command I recognise, try help"

    print "Thanks for using the application"
