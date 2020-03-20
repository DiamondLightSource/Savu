import os
import sys
import glob
import shutil

from setuptools import setup, find_packages

__version__ = None
__install__ = None
# loading the above parameters into the namespace from version.py
savu_path = os.path.abspath(os.path.dirname(__file__))
with open(savu_path + '/savu/version.py') as f:
    exec(f.read())

install_pkg = '.'.join(__install__.split('/'))


def readme():
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                           'README.rst')) as f:
        return f.read()

facility = 'dls'
facility_path = 'system_files/dls'


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

if '--facility' in sys.argv:
    index = sys.argv.index('--facility')
    sys.argv.pop(index)
    facility = sys.argv.pop(index)
    facility_path = 'system_files/'+facility
    _create_new_facility(facility_path)

if '--help' in sys.argv:
    print('To package for a facility use "--facility <facilityname> eg: python'
          'setup.py install --facility dls [Default facilityname is dls]')


def _get_packages():
    others = ['scripts',
              'scripts.config_generator',
              'scripts.log_evaluation',
              'scripts.citation_extractor',
              'install',
              install_pkg,
              install_pkg + '.conda-recipes',
              'test_data',
              'lib',
              'system_files',
              'plugin_examples']
    return find_packages() + others


mpi_all_files = glob.glob(os.path.join(facility_path, 'mpi', '*.sh'))
mpi_files = [mfile for mfile in mpi_all_files if 'dev' not in mfile]

setup(name='savu',
      version=__version__,
      description='Savu Python Tomography Pipeline',
      long_description=readme(),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering'
        'Operating System :: POSIX :: Linux'
      ],
      author='Mark Basham',
      author_email='scientificsoftware@diamond.ac.uk',
      license='Apache License, Version 2.0',
      packages=_get_packages(),

      scripts=mpi_files + [
               __install__ + '/tests/test_setup.sh',
               __install__ + '/tests/mpi_cpu_test.sh',
               __install__ + '/tests/mpi_gpu_test.sh',
               __install__ + '/tests/local_mpi_cpu_test.sh',
               __install__ + '/tests/local_mpi_gpu_test.sh'],

      entry_points={'console_scripts': [
                        'savu_config=scripts.config_generator.savu_config:main',
                        'savu=savu.tomo_recon:main',
                        'savu_quick_tests=savu:run_tests',
                        'savu_full_tests=savu:run_full_tests',
                        'savu_citations=scripts.citation_extractor.citation_extractor:main',
                        'savu_profile=scripts.log_evaluation.GraphicalThreadProfiler:main',
						'savu_param_extractor=scripts.savu_config.parameter_extractor:main',
						'savu_template_extractor=scripts.savu_config.hdf5_template_extractor:main',
						],},

      package_data={'test_data': [
                        'data/*',
                        'process_lists/*',
                        'test_process_lists/*',
                        'test_process_lists/vo_centering_test/*',
                        'data/i12_test_data/*',
                        'data/I18_test_data/*',
						'data/i18_templates/*',
                        'data/image_test/*',
                        'data/image_test/tiffs/*',
                        'data/full_field_corrected/*'],
                    'system_files': [
                        facility + '/*',
                        facility + '/mpi/*'],
                    'savu.test.travis.framework_tests': ['*.yml'],
                    'install': ['*.txt'],
                    __install__: ['*.txt'],
                    install_pkg + '.conda-recipes': [
                        'hdf5/*',
                        'h5py/*',
                        'savu/*',
                        'xraylib/*',
                        'astra/*',
                        'mpi4py/*']},

      include_package_data=True,
      zip_safe=False)
