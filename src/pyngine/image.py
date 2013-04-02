'''
import pygame

import time

from include import *
from pyngine import GameObject
from OpenGL import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class Texture(object):

    bound = None
    _all_loaded = {}
    def __init__(self, filename=None):

        self.filename = filename

        self.size = (0,0)

        if type(filename) is type(""):
            self._load_file()
        else:
            self._compile(filename)

    def _get_next_biggest(self, x, y):
        """Get the next biggest power of two x and y sizes"""
        if x == y == 1:
            return x, y
        nw = 16
        nh = 16
        while nw < x:
            nw *= 2
        while nh < y:
            nh *= 2
        return nw, nh

    def _load_file(self):
        """Loads file"""
        if not self.filename in self._all_loaded:
            image = pygame.image.load(self.filename)

            self._compile(image)
            if self.filename:
                self._all_loaded[self.filename] = [self]
        else:
            tex = self._all_loaded[self.filename][0]

            self.size = tex.size
            self.gl_tex = tex.gl_tex
            self._all_loaded[self.filename].append(self)

    def _compile(self, image):
        """Compiles image data into texture data"""

        self.gl_tex = glGenTextures(1)

        size = self._get_next_biggest(*image.get_size())

        image = pygame.transform.scale(image, size)

        tdata = pygame.image.tostring(image, "RGBA", 1)
        
        glBindTexture(GL_TEXTURE_2D, self.gl_tex)

        xx, xy = size
        self.size = size
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, xx, xy, 0, GL_RGBA,
                     GL_UNSIGNED_BYTE, tdata)

        if ANI_AVAILABLE:
            try:
                glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MAX_ANISOTROPY_EXT,glGetFloat(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT))
            except:
                pass

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    def bind(self):
        """Binds the texture for usage"""
        if not Texture.bound == self:
            glBindTexture(GL_TEXTURE_2D, self.gl_tex)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
            Texture.bound = self

    def __del__(self):
        """Clear the texture data"""
        if self.filename in self._all_loaded and\
           self in self._all_loaded[self.filename]:
            self._all_loaded[self.filename].remove(self)
            if not self._all_loaded[self.filename]:
                del self._all_loaded[self.filename]
                try:
                    glDeleteTextures([self.gl_tex])
                except:
                    pass #already cleared...


class BlankTexture(Texture):
    """A cached, blank texture."""
    _all_loaded = {}
    def __init__(self, size=(1,1), color=(1,1,1,1)):

        
        self.size = size
        self.filename = repr(size)+repr(color)
        self.gl_tex = None
        if self.filename in self._all_loaded:
            tex = self._all_loaded[self.filename][0]

            self.size = tex.size
            self.gl_tex = tex.gl_tex
            self._all_loaded[self.filename].append(self)
        else:
            i = pygame.Surface(size)
            if len(color) == 4:
                r, g, b, a = color
            else:
                r, g, b = color
                a = 1
            r *= 255
            g *= 255
            b *= 255
            a *= 255
            i.fill((r,g,b,a))
            
            self.gl_tex = glGenTextures(1)
            self._compile(i)

            self._all_loaded[self.filename] = [self]

class DisplayList(object):
    """An object to compile and store an OpenGL display list"""
    def __init__(self):
        """Creat the list"""
        self.gl_list = glGenLists(1)

    def begin(self):
        """Begin recording to the list - anything rendered after this will be compiled into the list and not actually rendered"""
        glNewList(self.gl_list, GL_COMPILE)

    def end(self):
        """End recording"""
        glEndList()

    def render(self):
        """Render the display list"""
        glCallList(self.gl_list)

    def __del__(self):
        """Clear the display list data"""
        try:
            glDeleteLists(self.gl_list, 1)
        except:
            pass #already cleared!

class VertexArray(object):
    """An object to store and render an OpenGL vertex array of vertices, colors and texture coords"""
    def __init__(self, render_type=None, max_size=100):
        """Create the array
           render_type is the OpenGL constant used in rendering, ie GL_POLYGON, GL_TRINAGLES, etc.
           max_size is the size of the array"""
        if render_type is None:
            render_type = GL_QUADS
        self.render_type = render_type
        self.texture = BlankTexture()

        self.max_size = max_size

        self.verts = numpy.empty((max_size, 3), dtype=object)
        self.colors = numpy.empty((max_size, 4), dtype=object)
        self.texcs = numpy.empty((max_size, 2), dtype=object)

    def render(self):
        """Render the array"""
        self.texture.bind()

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        glVertexPointer(3, GL_FLOAT, 0, self.verts)
        glColorPointer(4, GL_FLOAT, 0, self.colors)
        glTexCoordPointer(2, GL_FLOAT, 0, self.texcs)

        glDrawArrays(self.render_type, 0, self.max_size)

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

class FrameBuffer(object):
    """An object contains functions to render to a texture instead of to the main display.
       This object renders using FBO's, which are not available to everyone, but they are far faster and more versatile."""
    def __init__(self, size=(512,512), clear_color=(0,0,0,0)):
        """Create the FrameBuffer.
           size must be the (x,y) size of the buffer, will round up to the next power of two
           clear_color must be the (r,g,b) or (r,g,b,a) color of the background of the texture"""
        view.require_init()
        if not FBO_AVAILABLE:
            raise AttributeError("Frame buffer objects not available!")

        _x, _y = size
        x = y = 2
        while x < _x:
            x *= 2
        while y < _y:
            y *= 2
        size = x, y

        self.size = size
        self.clear_color = clear_color

        self.texture = BlankTexture(self.size, self.clear_color)

        if not bool(glGenRenderbuffersEXT):
            print("glGenRenderbuffersEXT doesn't exist")
            exit()
        self.rbuffer = glGenRenderbuffersEXT(1)
        glBindRenderbufferEXT(GL_RENDERBUFFER_EXT,
                              self.rbuffer)
        glRenderbufferStorageEXT(GL_RENDERBUFFER_EXT,
                                 GL_DEPTH_COMPONENT,
                                 size[0],
                                 size[1])

        self.fbuffer = glGenFramebuffersEXT(1)
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT,
                             self.fbuffer)
        glFramebufferTexture2DEXT(GL_FRAMEBUFFER_EXT,
                                  GL_COLOR_ATTACHMENT0_EXT,
                                  GL_TEXTURE_2D,
                                  self.texture.gl_tex,
                                  0)
        glFramebufferRenderbufferEXT(GL_FRAMEBUFFER_EXT,
                                     GL_DEPTH_ATTACHMENT_EXT,
                                     GL_RENDERBUFFER_EXT,
                                     self.rbuffer)

        self.worked = glCheckFramebufferStatusEXT(GL_FRAMEBUFFER_EXT) == GL_FRAMEBUFFER_COMPLETE_EXT

        glBindRenderbufferEXT(GL_RENDERBUFFER_EXT, 0)
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)

    def enable(self):
        """Turn this buffer on, swaps rendering to the texture instead of the display."""
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.fbuffer)
        r,g,b = self.clear_color[:3]
        glClearColor(r, g, b, 1)
        glClear(GL_DEPTH_BUFFER_BIT|GL_COLOR_BUFFER_BIT)

        glPushAttrib(GL_VIEWPORT_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glViewport(0,0,*self.size)
        gluPerspective(45, 1.0*self.size[0]/self.size[1], 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glEnable(GL_DEPTH_TEST)
        
    def disable(self):
        """Turn off the buffer, swap rendering back to the display."""
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)
        glClearColor(*view.screen.clear_color)
        glPopAttrib()

    def __del__(self):
        """Clean up..."""
        try:
            glDeleteFramebuffersEXT(1, [self.fbuffer])
        except:
            pass

        try:
            glDeleteRenderbuffersEXT(1, [self.rbuffer])
        except:
            pass

class TextureBuffer(object):
    """An object contains functions to render to a texture, using the main display.
       This object renders using the main display, copying to the texture, and then clearing.
       This object is considerably slower than teh FrameBuffer object, and less versatile,
       because you cannot use these objects mid-render, if you do you will lose whatever was rendered before them!"""
    def __init__(self, size=(512,512), clear_color=(0,0,0,0)):
        """Create the FrameBuffer.
           size must be the (x,y) size of the buffer, will round up to the next power of two
               if size is greater than the display size, it will be rounded down to the previous power of two
           clear_color must be the (r,g,b) or (r,g,b,a) color of the background of the texture"""
        _x, _y = size
        x = y = 2
        while x < _x:
            x *= 2
        while y < _y:
            y *= 2
        while x > view.screen.screen_size[0]:
            x /= 2
        while y > view.screen.screen_size[1]:
            y /= 2
        size = x, y

        self.size = size
        self.clear_color = clear_color

        self.texture = BlankTexture(self.size, self.clear_color)
        self.worked = True

    def enable(self):
        """Turn on rendering to this buffer, clears display buffer and preps it for this object."""
        r,g,b = self.clear_color[:3]

        glClearColor(r, g, b, 1)
        glClear(GL_DEPTH_BUFFER_BIT|GL_COLOR_BUFFER_BIT)
        glClearColor(*view.screen.clear_color)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glViewport(0,0,*self.size)
        gluPerspective(45, 1.0*self.size[0]/self.size[1], 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glEnable(GL_DEPTH_TEST)

    def disable(self):
        """Turn of this buffer, and clear the display."""
        self.texture.bind()
        glCopyTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 0,0,self.size[0], self.size[1], 0)

        glClear(GL_DEPTH_BUFFER_BIT|GL_COLOR_BUFFER_BIT)

class Material(object):
    """A simple class to store a color and texture for an object."""
    def __init__(self, name):
        """Create the material
           name is the name of the material"""
        self.name = name
        self.color = (1,1,1,1)
        self.texture = BlankTexture()

    def set_color(self, color):
        """Set color of material."""
        if len(color) == 3:
            color += (1,)
        self.color = color

    def copy(self):
        """Copy material."""
        a = Material(self.name)
        a.color = self.color
        a.texture = self.texture
        return a


class Image(GameObject):
    """A 2d image object"""
    def __init__(self, filename, pos=(0,0),
                 rotation=(0,0,0), scale=1,
                 colorize=(1,1,1,1)):
        """Create the Image
           filename must be a filename to an image file, a pygame.Surface object or an image.Image to copy
           pos is the 2d position of the image
           rotation is the 3d rotation of the image
           scale is the scale factor for the image
           colorize is the color of the image"""
        GameObject.__init__(self)
        self.filename = filename

        self.pos = pos

        if type(filename) is type(""):
            self._load_file()
        elif isinstance(filename, type(self)):
            self._image = filename._image
            self._pimage2 = filename._pimage2
            self._image_size = filename._image_size
            self._altered_image_size = filename._altered_image_size
            self.rect = self._image.get_rect()
            self.to_be_blitted = list(filename.to_be_blitted)
            self.display_list = filename.display_list
            self.texture = filename.texture
            self.offset = filename.offset
        else:
            self.compile_from_surface(filename)
            self.filename = None

        self.to_be_blitted = []
        self.rotation = rotation
        self.scale = scale
        self.colorize = colorize

    def copy(self):
        """Return a copy of the image - sharing the same data.DisplayList"""
        return Image(self, self.pos, self.rotation, self.scale, self.colorize)

    def _get_next_biggest(self, x, y):
        """Return next largest power of 2 size for an image"""
        nw = 16
        nh = 16
        while nw < x:
            nw *= 2
        while nh < y:
            nh *= 2
        return nw, nh

    def _load_file(self):
        """Load an image file"""
        self._image = pygame.image.load(self.filename)

        sx, sy = self._image.get_size()
        xx, xy = self._get_next_biggest(sx, sy)

        self._pimage2 = pygame.Surface((xx, xy)).convert_alpha()
        self._pimage2.fill((0,0,0,0))

        self._pimage2.blit(self._image, (0,0))
        self._pimage2 = pygame.transform.flip(self._pimage2, 0, 1)

        self._image_size = (sx, sy)
        self._altered_image_size = (xx, xy)

        self._texturize(self._pimage2)
        self.rect = self._image.get_rect()
        self._compile()

    def compile_from_surface(self, surf):
        """Prepare surf to be stored in a Texture and DisplayList"""
        self._image = surf
        sx, sy = self._image.get_size()
        xx, xy = self._get_next_biggest(sx, sy)

        self._pimage2 = pygame.Surface((xx, xy)).convert_alpha()
        self._pimage2.fill((0,0,0,0))

        self._pimage2.blit(self._image, (0,0))
        self._pimage2 = pygame.transform.flip(self._pimage2, 0, 1)

        self._image_size = (sx, sy)
        self._altered_image_size = (xx, xy)

        self.rect = self._image.get_rect()

        self._texturize(self._pimage2)
        self._compile()

    def _texturize(self, image):
        """Bind image to a data.Texture"""
        self.texture = data.Texture(image)

    def _compile(self):
        """Compile the Image into a data.DisplayList"""
        self.offset = self.get_width()/2, self.get_height()/2
        self.rect.center = self.offset[0] + self.pos[0], self.offset[1] + self.pos[1]

        self.display_list = data.DisplayList()
        self.display_list.begin()

        off = self.offset

        l = -off[0]
        r = off[0]
        t = -off[1]
        b = off[1]

        w = self.get_width()*1.0/self._altered_image_size[0]
        h = self.get_height()*1.0/self._altered_image_size[1]

        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex3f(l, t, 0)

        glTexCoord2f(0, h)
        glVertex3f(l, b, 0)

        glTexCoord2f(w, h)
        glVertex3f(r, b, 0)

        glTexCoord2f(w, 0)
        glVertex3f(r, t, 0)

        glEnd()

        self.display_list.end()

    def blit(self, other, pos):
        """Blit another image to this one at pos offset - ONLY allowing an image to blitted once
           other is another image.Image
           pos is the x,y offset of the blit"""
        self.remove_blit(other)
        self.to_be_blitted.append([other, pos])

    def blit_again(self, other, pos):
        """Same as blit, except you can blit the same image multiple times"""
        self.to_be_blitted.append([other, pos])

    def render(self, camera=None):
        """Render the image
           camera can be None or the camera the scene is using"""
        if not self.test_on_screen():
            return None

        ox, oy = self.offset
        h, w = self.get_size()

        pos = self.pos

        glPushMatrix()
        glTranslatef(pos[0]+ox, pos[1]+oy, 0)

        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)

        try:
            glScalef(self.scale[0], self.scale[1], 1)
        except:
            glScalef(self.scale, self.scale, 1)

        glColor(*self.colorize)
        self.texture.bind()
        if self.outline:
            misc.outline(self.display_list, self.outline_color, self.outline_size, True)
        self.display_list.render()
        glPopMatrix()
        if self.to_be_blitted:
            view.screen.push_clip2d((int(pos[0]), int(pos[1])), (int(w), int(h)))
            for i in self.to_be_blitted:
                x, y = i[1]
                x += pos[0]
                y += pos[1]
                o = i[0].pos
                i[0].pos = (x, y)
                i[0].render()
                i[0].pos = o
            view.screen.pop_clip()

    def get_width(self):
        """Return the width in pixels of the image"""
        return self._image_size[0]

    def get_height(self):
        """Return the height in pixels of the image"""
        return self._image_size[1]

    def get_size(self):
        """Return the width/height size of the image"""
        return self._image_size

    def get_rect(self):
        """Return a pygame.Rect of the image"""
        self.rect.center = self.offset[0] + self.pos[0], self.offset[1] + self.pos[1]
        return self.rect

    def clear_blits(self):
        """Remove all blits from the image"""
        self.to_be_blitted = []

    def remove_blit(self, image):
        """Remove all blits of image from the Image"""
        for i in self.to_be_blitted:
            if i[0] == image:
                self.to_be_blitted.remove(i)

    def sub_image(self, topleft, size):
        """Return a new Image object representing a smaller region of this Image."""
        image = self._image.subsurface(topleft, size)
        return Image(image, self.pos, self.rotation, self.scale, self.colorize)


class Image3D(Image):

    _all_loaded = {}
    def __init__(self, filename, pos=(0,0,0),
                 rotation=(0,0,0), scale=1,
                 colorize=(1,1,1,1)):
        """Create the Image3D
           filename must be a filename to an image file, or a pygame.Surface object
           pos is the 3d position of the image
           rotation is the 3d rotation of the image
           scale is the scale factor for the image
           colorize is the color of the image"""
        Image.__init__(self, filename, pos, rotation,
                       scale, colorize)

    def get_dimensions(self):
        """Return a tuple of (1,1,1) signifying the 3d dimensions of teh image - used by the quad tree"""
        return 1, 1, 1

    def get_pos(self):
        """Return the position of the Image3D"""
        return self.pos

    def get_scale(self):
        """Return the scale of the object."""
        try: return self.scale[0], self.scale[1], self.scale[2]
        except: return self.scale, self.scale, self.scale

    def render(self, camera=None):

        pos = self.pos

        glPushMatrix()
        glTranslatef(pos[0], pos[1], -pos[2])
        if camera:
            camera.set_facing_matrix()
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        try:
            glScalef(self.scale[0], self.scale[1], 1)
        except:
            glScalef(self.scale, self.scale, 1)
        glColor(*self.colorize)
        glDisable(GL_LIGHTING)
        self.texture.bind()
        if self.outline:
            misc.outline(self.display_list, self.outline_color, self.outline_size, True)
        self.display_list.render()
        if view.screen.lighting:
            glEnable(GL_LIGHTING)
        glPopMatrix()

    def blit(self, *args, **kwargs):
        print "Image3D does not support this function!"

    clear_blits = blit
    remove_blit = blit
    blit_again = blit
    test_on_screen = blit

    def copy(self):
        """Return a copy og the Image - sharing the same data.DisplayList"""
        return Image3D(self, self.pos, self.rotation, self.scale, self.colorize)

    def _load_file(self):
        """Load an image file"""
        self._image = pygame.image.load(self.filename)

        sx, sy = self._image.get_size()
        xx, xy = self._get_next_biggest(sx, sy)

        self._pimage2 = pygame.Surface((xx, xy)).convert_alpha()
        self._pimage2.fill((0,0,0,0))

        self._pimage2.blit(self._image, (0,0))

        self._pimage2 = pygame.transform.flip(self._pimage2, 0, 1)

        self._image_size = (sx, sy)
        self._altered_image_size = (xx, xy)

        self._texturize(self._pimage2)
        self._compile()
        self.rect = self._image.get_rect()

    def compile_from_surface(self, surf):
        """Prepare a pygame.Surface object for 3d rendering"""
        self._image = surf
        sx, sy = self._image.get_size()
        xx, xy = self._get_next_biggest(sx, sy)

        self._pimage2 = pygame.Surface((xx, xy)).convert_alpha()
        self._pimage2.fill((0,0,0,0))

        self._pimage2.blit(self._image, (0,0))

        self._pimage2 = pygame.transform.flip(self._pimage2, 0, 1)

        self._image_size = (sx, sy)
        self._altered_image_size = (xx, xy)

        self._texturize(self._pimage2)
        self._compile()

    def _compile(self):
        """Compile the rendering data into a data.DisplayList"""
        self.offset = self.get_width()/2, self.get_height()/2

        self.display_list = data.DisplayList()
        self.display_list.begin()

        w = self.get_width()*1.0/self._altered_image_size[0]
        h = self.get_height()*1.0/self._altered_image_size[1]

        gw, gh = self.get_size()

        if gw < gh:
            uw = gw * 1.0 / gh
            uh = 1
        elif gh < gw:
            uw = 1
            uh = gh * 1.0 / gw
        else:
            uw = uh = 1

        glBegin(GL_QUADS)
        glTexCoord2f(0, h)
        glVertex3f(-uw, -uh, 0)

        glTexCoord2f(w, h)
        glVertex3f(uw, -uh, 0)

        glTexCoord2f(w, 0)
        glVertex3f(uw, uh, 0)

        glTexCoord2f(0, 0)
        glVertex3f(-uw, uh, 0)
        glEnd()

        self.display_list.end()

    def sub_image(self, topleft, size):
        """Return a new Image3D object representing a smaller region of this Image3D."""
        image = self._image.subsurface(topleft, size)
        return Image3D(image, self.pos, self.rotation, self.scale, self.colorize)

def create_empty_image(size=(2,2), color=(1,1,1,1)):
    """Same as create_empty_texture, except returns an image.Image instead"""
    i = pygame.Surface(size).convert_alpha()
    if len(color) == 3:
        color = color + (1,)
    i.fill((255,255,255,255))
    return Image(i, colorize=color)

def create_empty_image3d(size=(2,2), color=(1,1,1,1)):
    """Same as create_empty_texture, except returns an image.Image3D instead"""
    i = pygame.Surface(size).convert_alpha()
    if len(color) == 3:
        color = color + (1,)
    i.fill((255,255,255,255))
    return Image3D(i, colorize=color)

class Animation(BaseSceneObject):
    """A simple object used to store, manipulate, animate and render a bunch of frames of 2d Image obejcts."""
    def __init__(self, frames=[], pos=(0,0),
                 rotation=(0,0,0), scale=1,
                 colorize=None):
        """Create the Animation
           frames must be a list/tuple of [Image, duration] objects
           pos is the 2d position of the image
           rotation is the 3d rotation of the image
           scale is the scale factor for the image
           colorize is the color of the image"""
        BaseSceneObject.__init__(self)

        self.frames = frames

        self.pos = pos
        self.rotation = rotation
        self.scale = scale
        self.colorize = colorize

        self.cur = 0
        self.ptime = time.time()
        self.running = True
        self.breakpoint = len(self.frames)-1
        self.startpoint = 0
        self.reversed = False
        self.looping = True

        self.filename = None

    def render(self, camera=None):
        """Render the animation - this also keeps track of swapping frames when they have run for their duration.
           camera must be None or the camera.Camera object used to render the scene."""
        if self.running:
            if time.time() - self.ptime > self.frames[self.cur][1]:
                if self.reversed:
                    self.cur -= 1
                    if self.cur < self.startpoint:
                        if self.looping:
                            self.cur = self.breakpoint
                        else:
                            self.cur += 1
                else:
                    self.cur += 1
                    if self.cur > self.breakpoint:
                        if self.looping:
                            self.cur = self.startpoint
                        else:
                            self.cur -= 1

                self.ptime = time.time()

        frame = self.current()
        frame.pos = self.pos
        frame.rotation = self.rotation
        frame.scale = self.scale
        frame.outline = self.outline
        frame.outline_size = self.outline_size
        frame.outline_color = self.outline_color
        if self.colorize:
            frame.colorize = self.colorize
        frame.render(camera)

    def seek(self, num):
        """'Jump' to a specific frame in the animation."""
        self.cur = num
        if self.cur < 0:
            self.cur = 0
        if self.cur >= len(self.frames):
            self.cur = len(self.frames)-1

        self.ptime = time.time()

    def set_bounds(self, start, end):
        """Set the start/end 'bounds' for playback, ie which range of frames to play."""
        if start < 0:
            start = 0
        if start >= len(self.frames):
            start = len(self.frames)-1
        if end < 0:
            end = 0
        if end >= len(self.frames):
            end = len(self.frames)-1
        if end < start:
            end = start
        self.startpoint = start
        self.breakpoint = end

    def pause(self):
        """Pause the running of the animation, and locks rendering to the current frame."""
        self.running = False

    def play(self):
        """Play the animation - only needed if pause has been called."""
        self.running = True
        self.ptime = time.time()

    def rewind(self):
        """Rewind the playback to first frame."""
        self.seek(0)

    def fastforward(self):
        """Fast forward playback to the last frame."""
        self.seek(self.length()-1)

    def get_width(self):
        """Return the width of the image."""
        return self.current().get_width()

    def get_height(self):
        """Return the height of the image."""
        return self.current().get_height()

    def get_size(self):
        """Return the width/height size of the image."""
        return self.current().get_size()

    def length(self):
        """Return the number of frames of the animation."""
        return len(self.frames)

    def reverse(self):
        """Reverse the playback of the image animation."""
        self.reversed = not self.reversed
    
    def reset(self):
        """Reset the image playback."""
        self.cur = 0
        self.ptime = time.time()
        self.reversed = False

    def loop(self, boolean=True):
        """Set looping of playback on/off - if looping is off animation will continue until the last frame and freeze."""
        self.looping = boolean
        self.ptime = time.time()

    def copy(self):
        """Return a copy of this Animation. Frames are shared..."""
        new = Animation(self.frames, self.pos, self.rotation, self.scale, self.colorize)
        new.running = self.running
        new.breakpoint = self.breakpoint
        new.startpoint = self.startpoint
        new.cur = self.cur
        new.ptime = self.ptime
        new.reversed = self.reversed
        new.looping = self.looping
        return new

    def current(self):
        """Return the current frame Image."""
        return self.frames[self.cur][0]

    def get_rect(self):
        """Return a pygame.Rect of the image"""
        frame = self.current()
        frame.pos = self.pos
        return frame.get_rect()

    def clear_blits(self):
        """Remove all blits from all frames of the image"""
        for i in self.frames:
            i[0].to_be_blitted = []

    def remove_blit(self, image):
        """Remove all blits of image from the Image"""
        for frame in self.frames:
            frame = frame[0]
            for i in frame.to_be_blitted:
                if i[0] == image:
                    frame.to_be_blitted.remove(i)

    def sub_image(self, topleft, size):
        """Return a new Image object representing a smaller region of the current frame of this Image."""
        return self.current().sub_image(topleft, size)

    def blit(self, other, pos):
        """Blit another image to this one at pos offset - ONLY allowing an image to blitted once
           other is another image.Image
           pos is the x,y offset of the blit"""
        for frame in self.frames:
            frame = frame[0]
            frame.remove_blit(other)
            frame.to_be_blitted.append([other, pos])

    def blit_again(self, other, pos):
        """Same as blit, except you can blit the same image multiple times"""
        for frame in self.frames:
            frame = frame[0]
            frame.to_be_blitted.append([other, pos])

class Animation3D(Animation):
    """3D version of Animation."""
    def __init__(self, frames=[], pos=(0,0,0), rotation=(0,0,0),
                 scale=1, colorize=(1,1,1,1)):
        """Create the Animation3D
           frames must be a list/tuple of [frame, duration] objects
           pos is the 3d position of the image
           rotation is the 3d rotation of the image
           scale is the scale factor for the image
           colorize is the color of the image"""
        Animation.__init__(self, frames, pos, rotation, scale, colorize)

    def blit(self, *args, **kwargs):
        print "Animation3D does not support this function!"

    clear_blits = blit
    remove_blit = blit
    blit_again = blit
    test_on_screen = blit

    def get_dimensions(self):
        """Return a tuple of (1,1,1) signifying the 3d dimensions of teh image - used by the quad tree"""
        return 1, 1, 1

    def get_pos(self):
        """Return the position of the Image3D"""
        return self.pos

    def get_scale(self):
        """Return the scale of the object."""
        try: return self.scale[0], self.scale[1], self.scale[2]
        except: return self.scale, self.scale, self.scale

    def copy(self):
        """Return a copy of this Animation. Frames are shared..."""
        new = Animation3D(self.frames, self.pos, self.rotation, self.scale, self.colorize)
        new.running = self.running
        new.breakpoint = self.breakpoint
        new.startpoint = self.startpoint
        new.cur = self.cur
        new.ptime = self.ptime
        new.reversed = self.reversed
        return new


def GIFImage(filename, pos=(0,0),
             rotation=(0,0,0), scale=1,
             colorize=(1,1,1,1)):
    """Load a GIF image into an Animation object if PIL is available, otherwise falls back to a static Image.
       filename must be the name of a gif image one disk
       pos is the 2d position of the image
       rotation is the 3d rotation of the image
       scale is the scale factor for the image
       colorize is the color of the image"""
    return Image(filename, pos, rotation, scale, colorize)


def GIFImage3D(filename, pos=(0,0,0),
               rotation=(0,0,0), scale=1,
               colorize=(1,1,1,1)):
    """Load a GIF image into an Animation3D object if PIL is available, otherwise falls back to a static Image3D.
       filename must be the name of a gif image one disk
       pos is the 3d position of the image
       rotation is the 3d rotation of the image
       scale is the scale factor for the image
       colorize is the color of the image"""
    return Image3D(filename, pos, rotation, scale, colorize)

def SpriteSheet(filename, frames=[], durations=100,
                pos=(0,0), rotation=(0,0,0), scale=1,
                colorize=(1,1,1,1)):
    """Load a "spritesheet" (basically, a flat 2d image that holds a lot of different images) into an Animation object.
       filename must be the name of an image on disk
       frames must be a tuple/list of [x,y,width,height] portions of the image that are unique frames
       durations must be a number or list/tuple of numbers representing the duration (in milliseconds) of all/each frame
       pos is the 2d position of the image
       rotation is the 3d rotation of the image
       scale is the scale factor for the image
       colorize is the color of the image"""
    if type(durations) in [type(1), type(1.2)]:
        durations = [durations]*len(frames)
    new = []
    image = pygame.image.load(filename).convert_alpha()

    for (frame, dur) in zip(frames, durations):
        new.append([Image(image.subsurface(*frame)), dur*0.001])

    return Animation(new, pos, rotation, scale, colorize)


def SpriteSheet3D(filename, frames=[], durations=[],
                  pos=(0,0), rotation=(0,0,0), scale=1,
                  colorize=(1,1,1,1)):
    """Load a "spritesheet" (basically, a flat 2d image that holds a lot of different images) into an Animation3D object.
       filename must be the name of an image on disk
       frames must be a tuple/list of [x,y,width,height] portions of the image that are unique frames
       durations must be a number or list/tuple of numbers representing the duration (in milliseconds) of all/each frame
       pos is the 3d position of the image
       rotation is the 3d rotation of the image
       scale is the scale factor for the image
       colorize is the color of the image"""
    if type(durations) in [type(1), type(1.2)]:
        durations = [durations]*len(frames)
    new = []
    image = pygame.image.load(filename).convert_alpha()

    for (frame, dur) in zip(frames, durations):
        new.append([Image3D(image.subsurface(*frame)), dur*0.001])

    return Animation3D(new, pos, rotation, scale, colorize)

def GridSpriteSheet(filename, frames=(1,1), duration=100,
                    pos=(0,0), rotation=(0,0,0), scale=1,
                    colorize=(1,1,1,1)):
    """Load a "spritesheet" (basically, a flat 2d image that holds a lot of different images) into an Animation object.
       filename must be the name of an image on disk
       frames must be a tuple/list of two ints, indicating the number of frames in the x/y axis
       duration must be a number representing the duration (in milliseconds) of all frames
       pos is the 2d position of the image
       rotation is the 3d rotation of the image
       scale is the scale factor for the image
       colorize is the color of the image"""
    new = []

    image = pygame.image.load(filename).convert_alpha()

    x_size = int(image.get_width() / frames[0])
    y_size = int(image.get_height() / frames[1])

    for x in xrange(frames[0]):
        for y in xrange(frames[1]):
            new.append([Image(image.subsurface(x*x_size, y*y_size, x_size, y_size)),
                        duration*0.001])
    return Animation(new, pos, rotation, scale, colorize)

def GridSpriteSheet3D(filename, frames=(1,1), duration=100,
                    pos=(0,0,0), rotation=(0,0,0), scale=1,
                    colorize=(1,1,1,1)):
    """Load a "spritesheet" (basically, a flat 2d image that holds a lot of different images) into an Animation object.
       filename must be the name of an image on disk
       frames must be a tuple/list of two ints, indicating the number of frames in the x/y axis
       duration must be a number representing the duration (in milliseconds) of all frames
       pos is the 2d position of the image
       rotation is the 3d rotation of the image
       scale is the scale factor for the image
       colorize is the color of the image"""
    new = []

    image = pygame.image.load(filename).convert_alpha()

    x_size = int(image.get_width() / frames[0])
    y_size = int(image.get_height() / frames[1])

    for x in xrange(frames[0]):
        for y in xrange(frames[1]):
            new.append([Image3D(image.subsurface(x*x_size, y*y_size, x_size, y_size)),
                        duration*0.001])
    return Animation3D(new, pos, rotation, scale, colorize)

def load_and_tile_resize_image(filename, size, pos=(0,0),
                               rotation=(0,0,0), scale=1,
                               colorize=(1,1,1,1), border_size=None):
    """Load an image, resize it by tiling
           (ie, each image is 9 tiles, and then the parts are scaled so that it fits or greator than size)
       filename must be the filename of the image to load
       size must be the (x, y) size of the image (may be larger)
       pos is the 2d position of the image
       rotation is the 3d rotation of the image
       scale is the scale factor of the image
       colorize is the color of the image
       Returns Image, tile_size"""
    image = pygame.image.load(filename).convert_alpha()
    x, y = size
    if x < image.get_width(): x = image.get_width()
    if y < image.get_height(): y = image.get_height()
    size = x, y
    if border_size:
        if border_size > int(min(image.get_size())/3):
            border_size = int(min(image.get_size())/3)
        x1=min((border_size, int(image.get_width()/3)))
        y1=min((border_size, int(image.get_height()/3)))
        x2 = image.get_width()-x1*2
        y2 = image.get_height()-y1*2
    else:
        x1=x2=int(image.get_width()/3)
        y1=y2=int(image.get_height()/3)

    topleft = image.subsurface((0, 0), (x1, y1))
    top = pygame.transform.scale(image.subsurface((x1, 0), (x2, y1)), (size[0]-x1*2, y1))
    topright = image.subsurface((x1+x2, 0), (x1,y1))

    left = pygame.transform.scale(image.subsurface((0, y1), (x1, y2)), (x1, size[1]-y1*2))
    middle = pygame.transform.scale(image.subsurface((x1, y1), (x2,y2)), (size[0]-x1*2, size[1]-y1*2))
    right = pygame.transform.scale(image.subsurface((x1+x2, y1), (x1,y2)), (x1, size[1]-y1*2))

    botleft = image.subsurface((0, y1+y2), (x1,y1))
    bottom = pygame.transform.scale(image.subsurface((x1, y1+y2), (x2, y1)), (size[0]-x1*2, y1))
    botright = image.subsurface((x1+y1, y1+y2), (x1,y1))

    new = pygame.Surface(size).convert_alpha()
    new.fill((0,0,0,0))
    new.blit(topleft, (0, 0))
    new.blit(top, (x1, 0))
    new.blit(topright, (size[0]-x1, 0))

    new.blit(left, (0, y1))
    new.blit(middle, (x1,y1))
    new.blit(right, (size[0]-x1, y1))

    new.blit(botleft, (0, size[1]-y1))
    new.blit(bottom, (x1, size[1]-y1))
    new.blit(botright, (size[0]-x1, size[1]-y1))
    return Image(new, pos, rotation, scale, colorize), (x1,y1)
'''