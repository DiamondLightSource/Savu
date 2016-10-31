from setuptools import setup, find_packages
import os

def readme():
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'README.rst')) as f:
        return f.read()

import sys
facility='dls'
facility_path='mpi/dls'
if '--facility' in sys.argv:
    index = sys.argv.index('--facility')
    sys.argv.pop(index)
    facility=sys.argv.pop(index)
    facility_path='mpi/'+facility
if '--help' in sys.argv:
    print 'To package for a facility use "--facility <facilityname>" eg: python setup.py install --facility dls [Default facilityname is dls]'

setup(name='savu',
      version='1.0',
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
      packages=find_packages()
      entry_points={'console_scripts':['savu_config=scripts.config_generator.savu_config:main','savu=savu.tomo_recon:main'],},
      scripts=[facility_path+'/savu_launcher.sh',facility_path+'/savu_mpijob.sh'],
      package_dir={'test_data':'test_data'},
      package_data={'test_data':['data/*.nxs','process_lists/*.nxs','test_process_lists/*.nxs']},
      include_package_data=True,
      zip_safe=False)
