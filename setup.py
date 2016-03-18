from setuptools import setup
import os

def readme():
    with open(os.path.abspath('./README.rst')) as f:
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
      version='0.3',
      description='Savu Python Tomography Pipeline',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering'
      ],
      author='Mark Basham',
      author_email='scientificsoftware@diamond.ac.uk',
      license='Apache License, Version 2.0',
      packages=['test_data','savu','savu.plugins','savu.core',
			'savu.core.transports',
			'savu.plugins.loaders',
			'savu.plugins.savers',
			'savu.plugins.corrections',
			'savu.plugins.reconstructions',
			'savu.plugins.driver',
			'savu.plugins.filters',
			'savu.data',
			'savu.data.transport_data',
			'scripts',
			'scripts.config_generator'],
      entry_points={'console_scripts':['savu_process_generator=scripts.config_generator.savu_config:main','tomo_recon=savu.tomo_recon:main'],},
      scripts=[facility_path+'/savu_launcher.sh',facility_path+'/savu_mpijob.sh'],
      package_dir={'test_data':'test_data'},
      package_data={'test_data':['data/*.nxs','process_lists/*.nxs','test_process_lists/*.nxs']},
      include_package_data=True,
      zip_safe=False)
