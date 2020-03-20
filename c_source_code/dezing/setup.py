from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(
    name='dezing',
    version='1.0',
    cmdclass={'build_ext': build_ext},
    ext_modules=[Extension("dezing", ["dezing.pyx"], libraries=["dezing"])],
)
