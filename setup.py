#!/usr/bin/env python

from distutils.core import setup
from pyngine import VERSION


long_description = '''Pyngine is a minimalist component-based game engine
for developing 3D Indie games easily for Linux, Mac OS X and Windows'''

setup(
    name = 'PyNgine',
    version = VERSION,
    license = 'GPLv3',
    description = 'Minimalist 3D game engine',
    long_description = long_description,
    author = 'Alejandro Rodas',
    author_email = 'alexrdp90@gmail.com',
    url = 'http://alexrdp90.github.com/pyngine',
    download_url = 'http://pypi.python.org/pypi/PyNgine',
    packages = ['pyngine'],
    package_dir = {'pyngine': 'src/pyngine'},
    package_data = {'pyngine': ['data/*']},
    requires = ['PyOpenGL'],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Games/Entertainment',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
