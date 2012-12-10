
PyNgine is a minimalist game engine written in Python, using the following modules:

* __Pygame__, a well-known set of modules designed for writing games in Python
* __PyOpenGL__, a cross platform layer between Python and [OpenGL](http://www.opengl.org/)
* __PyODE__, a Python bindings for [ODE (The Open Dynamics Engine)](http://www.ode.org/)


# Installation

## Prerequisites

For the installation of the required modules, it is recommended to have installed both 
`build-essential` and `pip`. In this guide I will use this software for the installation
of the modules.

	$ apt-get update 
	$ apt-get install build-essential
	$ apt-get install python-pip


## Installing Pygame

Since Pygame is not available on [PyPi](http://pypi.python.org/pypi), you can check out
the latest version for your platform on <http://www.pygame.org/download.shtml>.


## Installing OpenGL and PyOpenGL

	$ apt-get install freeglut3 freeglut3-dev
	$ pip install pyopengl


## Installing ODE and PyODE

First of all, you have to dowload the source from <http://sourceforge.net/projects/opende/files/>.
Once you have ODE installed, you can install the Python bindings directly from the package manager.

	$ cd ode-X.Y.Z
	$ ./configure
	$ make
	$ make install
	$ apt-get install python-ode-doc python-ode
