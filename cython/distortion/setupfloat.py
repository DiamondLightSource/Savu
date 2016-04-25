from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize
#$Id: setupfloat.py 447 2015-12-15 12:09:51Z kny48981 $
setup(
      name = "unwarp_app",
      ext_modules = cythonize('unwarp.pyx'),
   )

