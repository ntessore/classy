from distutils.core import setup
from distutils.extension import Extension
from distutils.errors import CompileError
from Cython.Distutils import build_ext

import numpy
import os
import sys
import subprocess

# custom builder
class _build_ext(build_ext):
    user_options = build_ext.user_options + [
        ('ompflag=', None, 'compiler flag for OpenMP'),
    ]

    def initialize_options(self):
        build_ext.initialize_options(self)
        self.ompflag = None

    def finalize_options(self):
        build_ext.finalize_options(self)
        if 'OMPFLAG' in os.environ:
            self.ompflag = os.environ['OMPFLAG']

    def run(self):
        # set the OMPFLAG in compiler options, unless empty
        if self.ompflag != '':
            for ext in self.extensions:
                ext.extra_compile_args.append(self.ompflag or '-fopenmp')
                ext.extra_link_args.append('-lomp')

        # make command in class_public, pass given OMPFLAG
        make = ['make', 'libclass.a']
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

# the extension for classy, OpenMP libraries are handled in builder
classy_ext = Extension('classy', ['class_public/python/classy.pyx'],
                       include_dirs=[numpy.get_include(), 'class_public/include'],
                       libraries=['class'], library_dirs=['class_public'])

# the setup script with one extension and the custom builder
setup(name='classy',
      version=CLASS_VERSION,
      description='Python interface to the Cosmological Boltzmann code CLASS',
      url='http://www.class-code.net',
      cmdclass={'build_ext': _build_ext},
      ext_modules=[classy_ext],
      #data_files=[('bbn', ['class_public/bbn/sBBN.dat'])]
)
