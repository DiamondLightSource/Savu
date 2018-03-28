from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
#$Id: setup.py 465 2016-02-16 11:02:36Z kny48981 $
setup(
      cmdclass={'build_ext':build_ext},
      ext_modules=[
         Extension("dezing",["dezing.pyx"],
            libraries=["dezing"])
         ]
      )
