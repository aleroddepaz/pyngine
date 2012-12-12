# Installation on Ubuntu

## Prerequisites

For the installation of the required modules, it is recommended to have installed both 
`build-essential` and `pip`. In this guide I will use this software for the installation
of the modules.

	$ apt-get update 
	$ apt-get install build-essential
	$ apt-get install python-pip
	# apt-get install python-dev


## Installing Pygame

Since Pygame is not available directly on [PyPi](http://pypi.python.org/pypi), you can check out
the latest version for your platform on <http://www.pygame.org/download.shtml>.


## Installing OpenGL and ODE

First of all, ODE checks if you have currently installed OpenGL, so if you want to add the ODE examples
to the installation, it is recommended to install OpenGL first.

	$ apt-get install freeglut3 freeglut3-dev

Secondly, download the source of ODE from <http://sourceforge.net/projects/opende/files/>.
Once you have ODE installed, then you can install the Python bindings directly from the package manager.

	$ cd ode-X.Y.Z
	$ ./configure
	$ make
	$ make install
	$ apt-get install python-ode-doc python-ode


## Installing PyNgine

To install PyNgine, which at the same time installs PyODE bindings, you have simply to run:

	$ pip install pyngine

Or if you are installing it directly from source:

	$ python setup.py install



# Installation on Fedora

	# Prerequisites
	$ yum install gcc				
	$ yum install python-pip
	$ yum install python-devel
	
	$ yum install pygame			# Pygame
	$ yum install freeglut			# OpenGL
	$ yum install ode				# ODE
	$ pip-python install pyopengl	# PyOpenGL / yum install python-opengl?
	$ pip-python install pyngine	# PyNgine
	
	# Download the PyODE source
	$ yum install ode-devel Pyrex
	$ cd PyODE-XYZ
	$ sudo ln -s /usr/lib/libstdc++.so.6 /usr/lib/libstdc++.so
	$ python setup.py build
	$ python setup.py install
