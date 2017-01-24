from setuptools import setup, find_packages
import os
import shutil

def readme():
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'README.rst')) as f:
        return f.read()

import sys
facility='dls'
facility_path='mpi/dls'

def _create_new_facility(facility_path):
    # if the folder doesn't exist then create it and add two template scripts...
    path=os.path.join(os.path.dirname(os.path.realpath(__file__)))
    facility_path = path+'/'+facility_path
    print "the facility path is", facility_path
    if not os.path.exists(facility_path):
        template_path = path+'/mpi/templates'
        print "Creating the directory...", facility_path
        os.makedirs(facility_path)
        print "Adding templates to the new directory..."
        shutil.copy(template_path+'/savu_launcher.sh', facility_path)
        shutil.copy(template_path+'/savu_mpijob.sh', facility_path)

if '--facility' in sys.argv:
    index = sys.argv.index('--facility')
    sys.argv.pop(index)
    facility=sys.argv.pop(index)
    facility_path='mpi/'+facility
    _create_new_facility(facility_path)
if '--help' in sys.argv:
    print 'To package for a facility use "--facility <facilityname>" eg: python setup.py install --facility dls [Default facilityname is dls]'

def _get_packages():
    others = ['scripts', 'scripts.config_generator', 'scripts.log_evaluation', 'scripts.citation_extractor',
              'install', 'install.conda-recipes', 'test_data', 'lib', 'mpi', 'plugin_examples']
    return find_packages() + others

setup(name='savu',
      version='1.2',
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
      install_requires=['pyreadline','colorama','h5py','mpi4py'],
      scripts=[facility_path+'/savu_launcher.sh',facility_path+'/savu_mpijob.sh', facility_path+'/savu_mpijob_local.sh',
               'install/savu_installer.sh', 'install/savu_setup.sh', 'install/mpi_cpu_test.sh', 'install/mpi_gpu_test.sh',
               'install/local_mpi_cpu_test.sh', 'install/local_mpi_gpu_test.sh'],
      entry_points={'console_scripts':['savu_config=scripts.config_generator.savu_config:main',
                    'savu=savu.tomo_recon:main', 'savu_quick_tests=savu:run_tests',
                    'savu_full_tests=savu:run_full_tests', 'savu_citations=scripts.citation_extractor.citation_extractor:main',
                    'savu_profile=scripts.log_evaluation.GraphicalThreadProfiler:main',],},
      package_data={'test_data':['data/*', 'process_lists/*','test_process_lists/*', 'data/i12_test_data/*',
                    'data/I18_test_data/*', 'data/image_test/*', 'data/image_test/tiffs/*'],'lib':['*.so'], 'mpi':['dls/*.sh'],
                    'install':['*.txt'], 'install.conda-recipes':['hdf5/*', 'h5py/*', 'savu/*', 'xraylib/*', 'astra/*']},
      include_package_data=True,
      zip_safe=False)

