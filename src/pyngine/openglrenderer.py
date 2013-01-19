import os
import pygame
from OpenGL.GL import * # @UnusedWildImport
from OpenGL.GLU import * # @UnusedWildImport



class OpenGLRenderer(object):
    """
    Class used as a facade to work with SDL
    and OpenGL capabilities
    """
    _screen = None
    _viewangle = 45
    _closeview = 0.1
    _farview = 100.0
    _clear_color = (.5, .5, .5, 1)
    _gl_lights = range(GL_LIGHT0, GL_LIGHT7 + 1)
    
    @classmethod
    def init(cls, screen_size, fullscreen):
        """
        Initializes SDL and OpenGL
        
        Parameters
        ----------
        screen_size : tuple
            2-tuple indicating widht and height of the screen
        fullscreen : bool
            Flag to set the window in full screen mode or not
        """
        pygame.init()
        params = pygame.OPENGL | pygame.DOUBLEBUF | pygame.HWSURFACE
        if fullscreen: params |= pygame.FULLSCREEN
        cls._screen = pygame.display.set_mode(screen_size, params)
        cls.resize(*screen_size)
        cls.enable()
        cls.define_settings()
    
    @classmethod
    def resize(cls, width, height):
        """
        Resizes the window according to the new width and height
        
        Parameters
        ----------
        width : int
        height : int
        """
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(cls._viewangle, float(width)/height,
                       cls._closeview, cls._farview)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    
    @classmethod
    def enable(cls):
        """
        Enables the GL capabilities needed
        """
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)
        glEnable(GL_NORMALIZE)
        glEnable(GL_BLEND)
        glEnable(GL_CULL_FACE)
    
    @classmethod
    def define_settings(cls):
        """
        Specifies the settings used for the GL capabilities
        """
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glShadeModel(GL_SMOOTH)
        glDepthFunc(GL_LEQUAL)
        glHint(GL_FOG_HINT, GL_NICEST)
        glPointSize(10)
        glClearColor(*cls._clear_color)
        glFrontFace(GL_CCW)
        glCullFace(GL_BACK)
        
    @classmethod
    def set_window_title(cls, title):
        """
        Sets the window title
        
        Parameters
        ----------
        title : str
        """
        pygame.display.set_caption(title)
        
    @classmethod
    def set_window_icon(cls, path):
        """
        Sets the window icon
        
        Parameters
        ----------
        path : str
            Path to the .ico file
        """
        if path is None:
            abspath = os.path.split(os.path.abspath(__file__))
            path = os.path.join(abspath[0], 'data', 'icon.ico')
        icon = pygame.image.load(path).convert_alpha()
        pygame.display.set_icon(icon)
        
    @classmethod
    def clearscreen(cls):
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

    @classmethod
    def flip(cls):
        pygame.display.flip()
        
    @classmethod
    def quit(cls):
        pygame.quit()
    
    @classmethod
    def getnextlight(cls):
        try: return cls._gl_lights.pop()
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
    
    @classmethod
    def render(cls, renderable):
        transform = renderable.transform
        a, b, c = transform.position
        w, x, y, z = transform.rotation
        x2 = x * x
        y2 = y * y
        z2 = z * z
        xy = x * y
        xz = x * z
        yz = y * z
        wx = w * x
        wy = w * y
        wz = w * z
        matrix = [1-2*(y2+z2), 2*(xy-wz), 2*(xz+wy), 0,
                  2*(xy+wz), 1-2*(x2+z2), 2*(yz-wx), 0,
                  2*(xz-wy), 2*(yz+wx), 1-2*(x2+y2), 0,
                  a, b, -c, 1]
        glPushMatrix()
        glMultMatrixf(matrix)
        if transform.scale != (1, 1, 1):
            glScalef(*transform.scale)
        if renderable.color is not None:
            glColor(*renderable.color)
        glCallList(renderable.gl_list)
        glPopMatrix()
    
    @classmethod
    def activate_fog(cls, color, density=.35, start=10., end=125.):
        glEnable(GL_FOG)
        glFogfv(GL_FOG_COLOR, color)
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogf(GL_FOG_DENSITY, density)
        glFogf(GL_FOG_START, start)
        glFogf(GL_FOG_END, end)
    
    @classmethod
    def desactivate_fog(cls):
        glDisable(GL_FOG)
    
    @classmethod
    def load_texture(cls, filename):
        texture_surface = pygame.image.load(filename)
        width, height = texture_surface.get_rect().size
        texture_data = pygame.image.tostring(texture_surface, 'RGB', True)
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, width, height, 0,
                     GL_RGB, GL_UNSIGNED_BYTE, texture_data)
        return texture_id
    
    @classmethod
    def delete_texture(cls, texture_id):
        glDeleteTextures(texture_id)
    
    @classmethod
    def do_2d_stuff(cls):
        glMatrixMode(GL_MODELVIEW)
        glDisable(GL_DEPTH_TEST)
        pygame.draw.aaline(cls._screen, (0,0,0), (0,0), (100,100))
        glEnable(GL_DEPTH_TEST)

