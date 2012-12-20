import os
import pygame
import OpenGL.GL as GL
import OpenGL.GLU as GLU

#TODO: Document class
class OpenGLRenderer(object):
    _screen_width = None
    _screen_height = None
    _aspect = 0
    _viewangle = 45
    _closeview = 0.1
    _farview = 100.0
    
    @classmethod
    def init(cls, screen_size, hwsurface, fullscreen):
        cls._screen_width = screen_size[0]
        cls._screen_height = screen_size[1]
        cls._aspect = 1. * screen_size[0] / screen_size[1]
        pygame.init()
        params = pygame.OPENGL | pygame.DOUBLEBUF
        if hwsurface:
            params |= pygame.HWSURFACE
        if fullscreen:
            params |= pygame.FULLSCREEN
        pygame.display.set_mode(screen_size, params)
        
    @classmethod
    def setwindowtitle(cls, title):
        pygame.display.set_caption(title)
        
    @classmethod
    def setwindowicon(cls, path):
        if path is None:
            abspath = os.path.split(os.path.abspath(__file__))
            path = os.path.join(abspath[0], 'data', 'icon.ico')
        icon = pygame.image.load(path).convert_alpha()
        pygame.display.set_icon(icon)
        
    @classmethod
    def initmodelviewmatrix(cls):
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        
    @classmethod
    def clearscreen(cls):
        GL.glClear(GL.GL_DEPTH_BUFFER_BIT | GL.GL_COLOR_BUFFER_BIT)
        
    @classmethod
    def enable(cls):
        GL.glEnable(GL.GL_FOG)
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glEnable(GL.GL_COLOR_MATERIAL)
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_NORMALIZE)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_BLEND)
        GL.glEnable(GL.GL_SCISSOR_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        
    @classmethod
    def setviewport(cls):
        GL.glViewport(0, 0, cls._screen_width, cls._screen_height)
        
    @classmethod
    def setperspective(cls):
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluPerspective(cls._viewangle, cls._aspect,
                       cls._closeview, cls._farview)
        
    @classmethod
    def dostuff(cls):
        GL.glColorMaterial(GL.GL_FRONT, GL.GL_AMBIENT_AND_DIFFUSE)
        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glHint(GL.GL_PERSPECTIVE_CORRECTION_HINT, GL.GL_NICEST)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glPointSize(10)
        GL.glClear(GL.GL_DEPTH_BUFFER_BIT | GL.GL_COLOR_BUFFER_BIT)
        GL.glFogfv(GL.GL_FOG_COLOR, (.5, .5, .5, 1))
        GL.glFogi(GL.GL_FOG_MODE, GL.GL_LINEAR)
        GL.glFogf(GL.GL_FOG_DENSITY, .35)
        GL.glHint(GL.GL_FOG_HINT, GL.GL_NICEST)
        GL.glFogf(GL.GL_FOG_START, 10.0)
        GL.glFogf(GL.GL_FOG_END, 125.0)
        GL.glAlphaFunc(GL.GL_GEQUAL, .5)
        GL.glClearColor(.5, .5, .5, 1)
        GL.glTexEnvi(GL.GL_TEXTURE_ENV, GL.GL_TEXTURE_ENV_MODE, GL.GL_MODULATE)
        GL.glFrontFace(GL.GL_CCW)
        GL.glCullFace(GL.GL_BACK)
        
    @classmethod
    def flip(cls):
        pygame.display.flip()
        
    @classmethod
    def quit(cls):
        pygame.quit()
    
    _gllights = range(GL.GL_LIGHT0, GL.GL_LIGHT7 + 1) # Max 8 lights
    
    @classmethod
    def getnextlight(cls):
        try: return cls._gllights.pop()
        except IndexError: return None

    @classmethod
    def enablelight(cls, gl_light, ambient, diffuse,
                    specular, spot_direction, gl_position):
        GL.glLightfv(gl_light, GL.GL_AMBIENT, ambient)
        GL.glLightfv(gl_light, GL.GL_DIFFUSE, diffuse)
        GL.glLightfv(gl_light, GL.GL_SPECULAR, specular)
        GL.glLightfv(gl_light, GL.GL_SPOT_DIRECTION, spot_direction)
        GL.glLightfv(gl_light, GL.GL_POSITION, gl_position)
        GL.glEnable(gl_light)
    
    @classmethod
    def disable(cls, foo):
        GL.glDisable(foo)
    
    @classmethod
    def render(cls, renderable):
        transform = renderable.transform
        x, y, z = transform.position
        R = transform.rotation
        rot = [R[0], R[3], R[6], 0,
               R[1], R[4], R[7], 0,
               R[2], R[5], R[8], 0,
               x, y, -z, 1]
        GL.glPushMatrix()
        GL.glMultMatrixd(rot)
        if transform.scale != (1, 1, 1):
            GL.glScalef(*transform.scale)
        if renderable.color is not None:
            GL.glColor(*renderable.color)
        GL.glCallList(renderable.gl_list)
        GL.glPopMatrix()
