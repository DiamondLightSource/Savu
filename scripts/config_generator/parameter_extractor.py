#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 15:42:30 2019

@author: qmm55171
"""

import argparse

from scripts.config_generator.content import Content


def arg_parser():
    """ Arg parser for command line arguments.
    """
    parser = argparse.ArgumentParser(prog='update_template')
    parser.add_argument('nxsfile', help='The nexus file')
    parser.add_argument('plugin', help='Plugin name')
    parser.add_argument('param', help='plugin parameter name')
    return parser.parse_args()

def get_parameter_value(nxsfile, plugin_name, plugin_param):
    content = Content()
    content.fopen(nxsfile)
    plist = content.plugin_list.plugin_list
    
    for plugin in plist:
        if plugin['name'] == plugin_name:
            if plugin_param in list(plugin['data'].keys()):
                print(plugin_name, plugin['data'][plugin_param])

if __name__ == '__main__':
    arg = arg_parser()
    get_parameter_value(arg.nxsfile, arg.plugin, arg.param)
