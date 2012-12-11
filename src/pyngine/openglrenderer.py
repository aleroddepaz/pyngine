import os
import pygame
from OpenGL.GL import * # @UnusedWildImport
from OpenGL.GLU import * # @UnusedWildImport


class OpenGLRenderer(object):
    _screenwidth = None
    _screenheight = None
    _aspect = 0
    _viewangle = 45
    _closeview = 0.1
    _farview = 100.0
    
    @classmethod
    def init(cls, screensize, hwsurface):
        cls._screenwidth = screensize[0]
        cls._screenheight = screensize[1]
        cls._aspect = 1. * screensize[0] / screensize[1]
        pygame.init()
        params = pygame.OPENGL | pygame.DOUBLEBUF
        if hwsurface:
            params |= pygame.HWSURFACE
        pygame.display.set_mode(screensize, params)
        
    @classmethod
    def setwindowtitle(cls, title):
        pygame.display.set_caption(title)
        
    @classmethod
    def setwindowicon(cls, path):
        if path is None:
            abspath = os.path.split(os.path.abspath(__file__))
            path = os.sep.join([abspath[0], 'data', 'icon.ico'])
        icon = pygame.image.load(path).convert_alpha()
        pygame.display.set_icon(icon)
        
    @classmethod
    def initmodelviewmatrix(cls):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
    @classmethod
    def clearscreen(cls):
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
        
    @classmethod
    def enable(cls):
        glEnable(GL_FOG)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)
        glEnable(GL_NORMALIZE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glEnable(GL_SCISSOR_TEST)
        glEnable(GL_CULL_FACE)
        
    @classmethod
    def setviewport(cls):
        glViewport(0, 0, cls._screenwidth, cls._screenheight)
        
    @classmethod
    def setperspective(cls):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(cls._viewangle, cls._aspect,
                       cls._closeview, cls._farview)
        
    @classmethod
    def dostuff(cls):
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
        glShadeModel(GL_SMOOTH)
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glPointSize(10)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
        glFogfv(GL_FOG_COLOR, (.5, .5, .5, 1))
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogf(GL_FOG_DENSITY, .35)
        glHint(GL_FOG_HINT, GL_NICEST)
        glFogf(GL_FOG_START, 10.0)
        glFogf(GL_FOG_END, 125.0)
        glAlphaFunc(GL_GEQUAL, .5)
        glClearColor(.5, .5, .5, 1)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glFrontFace(GL_CCW)
        glCullFace(GL_BACK)
        
    @classmethod
    def flip(cls):
        pygame.display.flip()
        
    @classmethod
    def quit(cls):
        pygame.quit()
    
    _gllights = range(GL_LIGHT0, GL_LIGHT7 + 1) # Max 8 lights
    
    @classmethod
    def getnextlight(cls):
        try: return cls._gllights.pop()
        except IndexError: return None

    @classmethod
    def enablelight(cls, gl_light, ambient, diffuse,
                    specular, spot_direction, gl_position):
        glLightfv(gl_light, GL_AMBIENT, ambient)
        glLightfv(gl_light, GL_DIFFUSE, diffuse)
        glLightfv(gl_light, GL_SPECULAR, specular)
        glLightfv(gl_light, GL_SPOT_DIRECTION, spot_direction)
        glLightfv(gl_light, GL_POSITION, gl_position)
        glEnable(gl_light)
    
    @classmethod
    def disable(cls, foo):
        glDisable(foo)
