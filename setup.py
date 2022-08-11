import os
import sys
import glob
import shutil

from setuptools import setup, find_packages
from savu.test.test_process_list_utils import get_all_files_from

facility = 'dls'
facility_path = 'system_files/dls'
utils_path = 'savu/plugins/loaders/utils'
templates_path = 'savu/plugins/loaders/templates/'
plugin_guide_path = 'doc/source/plugin_guides/plugins'

from savu.version import __version__, __install__

def readme():
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                           'README.rst')) as f:
        return f.read()


def _create_new_facility(facility_path):
    #  if the folder doesn't exist then create it and add two template scripts
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    facility_path = path+'/'+facility_path
    dls_path = path+'/system_files/dls'
    if not os.path.exists(facility_path):
        os.makedirs(facility_path)

        for root, dirs, files in os.walk(dls_path):
            folder = os.path.relpath(root, dls_path)
            to_this_folder = os.path.join(facility_path, folder)
            if not os.path.exists(to_this_folder):
                os.makedirs(to_this_folder)
            for f in files:
                copy_this_file = os.path.join(root, f)
                shutil.copy(copy_this_file, to_this_folder)

    else:
        dls_sys_params = os.path.join(dls_path, 'system_parameters.yml')
        facility_sys_params = \
            os.path.join(facility_path, 'system_parameters.yml')
        if not os.path.exists(facility_sys_params):
            shutil.copy(dls_sys_params, facility_path)

def get_files(fpath):
    files = [os.path.join(fpath, d) for d in get_all_files_from(fpath)]
    return [(os.path.dirname(d), [d]) for d in files]


if '--facility' in sys.argv:
    index = sys.argv.index('--facility')
    sys.argv.pop(index)
    facility = sys.argv.pop(index)
    facility_path = 'system_files/'+facility
    _create_new_facility(facility_path)


if '--help' in sys.argv:
    print('To package for a facility use "--facility <facilityname> eg: python'
          'setup.py install --facility dls [Default facilityname is dls]')

mpi_all_files = glob.glob(os.path.join(facility_path, 'mpi', '*.sh'))
mpi_files = [mfile for mfile in mpi_all_files if 'dev' not in mfile]
install_test_files = glob.glob(os.path.join('install/tests', '*.sh'))
all_templates=glob.glob(templates_path + "/**/*.yml", recursive = True)

# data file locations
version_file = os.path.join(__install__, 'version.txt')
env_file = os.path.join(__install__, 'environment.yml')
sys_file = os.path.join(facility_path, "system_parameters.yml")
utils_file = os.path.join(utils_path, "yaml_config.yaml")
mod_file = os.path.join(facility_path, "modulefile", __version__)
mod_file = [mod_file] if os.path.exists(mod_file) else []
conda_recipes = get_files(os.path.join(__install__, '..', 'conda-recipes'))
test_data = get_files("test_data")
plugin_guides = get_files(plugin_guide_path)


setup(name='savu',
      version=__version__,
      description='Savu Python Tomography Pipeline',
      long_description=readme(),
      url='https://github.com/DiamondLightSource/Savu',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: Apache Software License',
          'Natural Language :: English',
          'Programming Language :: Python :: 3.7',
          'Topic :: Scientific/Engineering'
          'Operating System :: POSIX :: Linux'
      ],
      author='Mark Basham',
      author_email='scientificsoftware@diamond.ac.uk',
      license='Apache License, Version 2.0',
      packages=find_packages(),

      scripts=mpi_files + install_test_files + all_templates,

      entry_points={'console_scripts': [
          'savu_config=scripts.config_generator.savu_config:main',
          'savu_plugin_generator=scripts.plugin_generator.savu_plugin_generator:main',
          'savu_mod=scripts.savu_mod.savu_mod:command_line_modify',
          'savu_refresh=scripts.refresh_process_lists.savu_refresh_process_lists:refresh_lists',
          'savu=savu.tomo_recon:main',
          'refresh_lists=savu:run_refresh_lists',
          'savu_quick_tests=savu:run_tests',
          'savu_full_tests=savu:run_full_tests',
          'savu_citations=scripts.citation_extractor.citation_extractor:main',
          'savu_profile=scripts.log_evaluation.GraphicalThreadProfiler:main',
          'savu_param_extractor=scripts.savu_config.parameter_extractor:main',
          'savu_template_extractor=scripts.savu_config.hdf5_template_extractor:main',
          'savu_pre_run=savu.pre_run:main',
      ], },

      package_data={
           'savu.test.travis.framework_tests': ['*.yml'],
      },

      data_files=[('htmls', ['scripts/log_evaluation/string_single.html']),
                  ('htmls', ['scripts/log_evaluation/string_multi.html']),
                  ('htmls', ['scripts/log_evaluation/testing.html']),
                  ('css', ['scripts/log_evaluation/style_sheet.css']),
                  (os.path.dirname(version_file), [version_file]),
                  (os.path.dirname(sys_file), [sys_file]),
                  (os.path.dirname(utils_file), [utils_file]),
                      (os.path.dirname(env_file), [env_file])] \
                  + conda_recipes + test_data + mod_file + plugin_guides,

      include_package_data=True,
      zip_safe=False)
