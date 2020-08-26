from distutils.core import setup
from distutils.extension import Extension
from distutils.errors import CompileError
from distutils.sysconfig import get_python_lib
from Cython.Distutils import build_ext

import numpy
import os
import sys
import subprocess

# custom builder
class _build_ext(build_ext):
    user_options = build_ext.user_options + [
        ('ompflag=', None, 'compiler flag for OpenMP'),
        ('omplib=', None, 'library for OpenMP'),
    ]

    def initialize_options(self):
        build_ext.initialize_options(self)
        self.ompflag = None
        self.omplib = '-lgomp'

    def finalize_options(self):
        build_ext.finalize_options(self)
        if 'OMPFLAG' in os.environ:
            self.ompflag = os.environ['OMPFLAG']
        if 'OMPLIB' in os.environ:
            self.ompflag = os.environ['OMPLIB']

    def run(self):
        # set the OMPFLAG and OMPLIB in compiler options, unless empty
        if self.ompflag != '':
            for ext in self.extensions:
                ext.extra_compile_args.append(self.ompflag or '-fopenmp')
                ext.extra_link_args.append(self.omplib)

        # get the directory where the package will be installed (MDIR)
        # as well as the current working directory (WRKDIR)
        mdir = os.path.join(get_python_lib(), 'classy')
        wrkdir = 'build'

        # make command in class_public, pass options
        make = ['make', 'libclass.a', 'MDIR=' + mdir, 'WRKDIR=' + wrkdir]
        if self.ompflag is not None:
            make += ['OMPFLAG=' + self.ompflag]

        # call make in class_public
        try:
            subprocess.check_output(make, cwd='class_public')
        except subprocess.CalledProcessError as e:
            raise CompileError(e.output)

        # build extension as usual
        build_ext.run(self)


# call make in wrapper to build version tool, then call it
subprocess.check_call(['make'])
CLASS_VERSION = subprocess.check_output(['./version']).decode(sys.stdout.encoding)

# source files for the classy extension
CLASSY_SOURCES = [
    'class_public/python/classy.pyx',
]

# include paths for the classy extension
CLASSY_INCLUDE_DIRS = [
    numpy.get_include(),
    'class_public/include',
]

# libraries for the classy extension
CLASSY_LIBRARIES = [
    'class',
    'm',
]

# library search dirs for the classy extension
CLASSY_LIBRARY_DIRS = [
    'class_public',
]

# subdirectories with data files
CLASS_DATA_PACKAGES = [
    'classy.bbn',
]

# the setup script with one extension and the custom builder
setup(
    name='classy',
    version=CLASS_VERSION,
    description='Python interface to the Cosmological Boltzmann code CLASS',
    url='http://www.class-code.net',
    cmdclass={'build_ext': _build_ext},
    ext_modules=[
        Extension(
            'classy',
            CLASSY_SOURCES,
            include_dirs=CLASSY_INCLUDE_DIRS,
            libraries=CLASSY_LIBRARIES,
            library_dirs=CLASSY_LIBRARY_DIRS
        ),
    ],
    packages=CLASS_DATA_PACKAGES,
    package_dir={'classy': 'class_public'},
    package_data={'': ['*.dat']}
)
