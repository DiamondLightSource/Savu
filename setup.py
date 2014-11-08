from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='savu',
      version='0.1',
      description='Savu Python Tomography Pipeline',
      long_description=readme(),
      classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering'
      ],
      author='Mark Basham',
      author_email='scientificsoftware@diamond.ac.uk',
      license='Apache License, Version 2.0',
      packages=['savu',
                'savu.core',
                'savu.data',
                'savu.mpi_test',
                'savu.mpi_test.dls',
                'savu.plugins',
                'savu.test'],
      include_package_data=True,
      zip_safe=False)