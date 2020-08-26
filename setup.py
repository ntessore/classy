from distutils.core import setup
from distutils.extension import Extension
from distutils.command.build import build
from distutils.errors import CompileError
from Cython.Distutils import build_ext

import numpy
import os
import sys
import subprocess

class my_build(build):
    user_options = build.user_options + [
        ('ompflag=', None, 'compiler flag for OpenMP'),
    ]

    def initialize_options(self):
        build.initialize_options(self)
        self.ompflag = None

    def finalize_options(self):
        build.finalize_options(self)
        if 'OMPFLAG' in os.environ:
            self.ompflag = os.environ['OMPFLAG']

    def run(self):
        make = ['make', 'libclass.a']
        if self.ompflag is not None:
            make += ['OMPFLAG=' + self.ompflag]
        try:
            subprocess.check_output(make, cwd='class_public')
        except subprocess.CalledProcessError as e:
            raise CompileError(e.output)
        build.run(self)

subprocess.check_call(['make'])
CLASS_VERSION = subprocess.check_output(['./version']).decode(sys.stdout.encoding)

classy_ext = Extension('classy', ['class_public/python/classy.pyx'],
                       include_dirs=[numpy.get_include(), 'class_public/include'],
                       libraries=['class'], library_dirs=['class_public'])

setup(name='classy',
      version=CLASS_VERSION,
      description='Python interface to the Cosmological Boltzmann code CLASS',
      url='http://www.class-code.net',
      cmdclass={'build': my_build, 'build_ext': build_ext},
      ext_modules=[classy_ext],
      #data_files=[('bbn', ['class_public/bbn/sBBN.dat'])]
)
