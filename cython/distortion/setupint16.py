from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize
#$Id: setupint16.py 446 2015-12-15 12:08:48Z kny48981 $
setup(
      name = "unwarpint16_app",
      ext_modules = cythonize('unwarpint16.pyx'),
   )

