#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 15:42:30 2019

@author: qmm55171
"""

import os
import sys
import argparse

from savu.data.meta_data import MetaData
from scripts.config_generator.content import Content
from savu.plugins.loaders.yaml_converter import YamlConverter


def arg_parser():
    """ Arg parser for command line arguments.
    """
    parser = argparse.ArgumentParser(prog='update_template')
    parser.add_argument('nxsfile', help='The nexus file')
    key_help = 'Full stop separated key for dictionary entry'
    parser.add_argument("-k", "--key", help=key_help, default=None)
    return parser.parse_args()


def get_parameter_value(nxsfile, plugin_name, plugin_param):
    content = Content()
    content.fopen(nxsfile)
    plist = content.plugin_list.plugin_list

    found_params = []
    for plugin in plist:
        if plugin['name'] == plugin_name:
            if plugin_param in list(plugin['data'].keys()):
                found_params.append(plugin['data'][plugin_param])

    return found_params


def check_yaml_path(paths):
    paths = [os.path.abspath(p) for p in paths]
    for p in paths:
        if not os.path.isfile(p):
            raise Exception("Template file not found at %s" % p)
    return paths


def get_data_dict(paths):
    all_data_dict = {}
    yu = YamlConverter()
    for p in paths:
        yu.parameters['yaml_file'] = p
        all_data_dict.update(yu.setup(template=True))
    return all_data_dict


def get_string_result(key, data_dict, mData, res=[]):
    if '*' in key:
        for data in list(data_dict.keys()):
            res = get_string_result(
                    key.replace('*', data), data_dict, mData, res)
    else:
        res.append(mData.get(key.split('.')))
    return res


if __name__ == '__main__':
    arg = arg_parser()
    # find all Hdf5TemplateLoaders
    plugin = 'Hdf5TemplateLoader'
    param = 'yaml_file'
    paths = check_yaml_path(get_parameter_value(arg.nxsfile, plugin, param))
    data_dict = get_data_dict(paths)
    res = get_string_result(arg.key, data_dict, MetaData(data_dict))
    print(','.join(res))

    