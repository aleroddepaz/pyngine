#!/usr/bin/env python
from distutils.core import setup

setup(
    name = 'PyNgine',
    version = '0.0.2',
    license = 'GPLv3',
    description = 'Minimalist 3D game engine',
    author = 'Alejandro Rodas',
    author_email = 'alexrdp90@gmail.com',
    packages = ['pyngine'],
    package_dir = {'pyngine': 'src/pyngine'},
    package_data = {'pyngine': ['data/*']},
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Games/Entertainment'
    ],
)
