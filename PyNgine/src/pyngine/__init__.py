import os
import pygame
from OpenGL.GL import * # @UnusedWildImport
from OpenGL.GLU import * # @UnusedWildImport
from OpenGL.raw.GLUT import glutSolidCube, glutSolidSphere
from physics import PhysicsEngine
from input import Input



# ==============================
# Component & Subclasses
# ==============================

class Component(object):
    def __init__(self):
        self.gameobject = None
    @property
    def transform(self):
        return self.gameobject.transform
    @property
    def rigidbody(self):
        return self.gameobject.rigidbody
    @property
    def collider(self):
        return self.gameobject.collider
    def start(self):
        pass
    def update(self):
        pass
    def oncollision(self, other):
        pass
    def handlemessage(self, string, data):
        pass


class Renderer(Component):
    def __init__(self, color):
        Component.__init__(self)
        self.gl_list = glGenLists(1)
        self.color = color
    def render(self):
        x, y, z = self.transform.position
        R = self.transform.rotation
        rot = [R[0], R[3], R[6], 0,
               R[1], R[4], R[7], 0,
               R[2], R[5], R[8], 0,
               x, y, -z, 1]
        glPushMatrix()
        glMultMatrixd(rot)
        if self.transform.scale != (1, 1, 1):
            glScalef(*self.transform.scale)
        glColor(*self.color)
        glCallList(self.gl_list)
        glPopMatrix()


class Sphere(Renderer):
    slices = 18
    stacks = 18
    def __init__(self, color=(0, 0, 0, 1)):
        Renderer.__init__(self, color)
        glNewList(self.gl_list, GL_COMPILE)
        glutSolidSphere(.5, Sphere.slices, Sphere.stacks)
        glEndList()


class Cube(Renderer):
    def __init__(self, color=(0, 0, 0, 1)):
        Renderer.__init__(self, color)
        glNewList(self.gl_list, GL_COMPILE)
        glutSolidCube(1)
        glEndList()


class Rigidbody(Component):
    def __init__(self, density):
        Component.__init__(self)
        self.density = density
        self._body = PhysicsEngine.createbody()
    def start(self):
        mass = PhysicsEngine.createmass()
        mass.setBox(self.density, *self.transform.scale)
        self._body.setMass(mass)
        self._body.setPosition(self.transform.position)
        self._body.setRotation(self.transform.rotation)
        self.transform._setbody(self._body)
        if self.collider is not None:
            self.collider._setbody(self._body)
    def addforce(self, force):
        self._body.addForce(force)
    def isenabled(self):
        return self._body.isEnabled() == 1
    @property
    def usegravity(self):
        return self._body.getGravityMode()
    @usegravity.setter
    def usegravity(self, value):
        self._body.setGravityMode(value)
    @property
    def velocity(self):
        return self._body.getLinearVel()
    @velocity.setter
    def velocity(self, value):
        self._body.setLinearVel(value)


class Collider(Component):
    def __init__(self):
        Component.__init__(self)
        self._geom = None
    def _latestart(self):
        self._geom.gameobject = self.gameobject
    def _setbody(self, body):
        self._geom.setBody(body)
    def _clearbody(self):
        self._geom.setBody(None)


class BoxCollider(Collider):
    def __init__(self):
        Collider.__init__(self)
    def start(self):
        scale = self.transform.scale
        self._geom = PhysicsEngine.creategeom("Box", (scale,))
        self._latestart()


class SphereCollider(Collider):
    def __init__(self):
        Collider.__init__(self)
    def start(self):
        radius = self.transform.scale[0]/2.
        self._geom = PhysicsEngine.creategeom("Sphere", (radius,))
        self._latestart()


class Transform(Component):
    
    def __init__(self, position=(0, 0, 0), rotation=(0,)*9, scale=(1, 1, 1)):
        Component.__init__(self)
        self.__position = position
        self.__rotation = rotation
        self.__scale = scale
        self.__body = None
    
    def _setbody(self, body):
        self.__body = body
        
    def _clearbody(self):
        self.__body = None
        
    @property
    def position(self):
        if self.__body is not None:
            return self.__body.getPosition()
        return self.__position
    
    @position.setter
    def position(self, value):
        if self.__body is not None:
            self._body.setPosition(value)
        self.__position = value
    
    @property
    def rotation(self):
        if self.__body is not None:
            return self.__body.getRotation()
        return self.__rotation
    
    @rotation.setter
    def rotation(self, value):
        if self.__body is not None:
            self._body.setRotation(value)
        self.__rotation = value

    @property
    def scale(self):
        return self.__scale
    
    @scale.setter
    def scale(self, value):
        self.__scale = value

    def move(self, movement):
        self.position = tuple(map(sum, zip(self.position, movement)))

    def rotate(self, rotation):
        self.rotation = tuple(map(sum, zip(self.rotation, rotation)))


class Camera(Component):
    def __init__(self, distance=(0, 0, 0), orientation=(0, 0, 0)):
        Component.__init__(self)
        self.distance = distance
        self.orientation = orientation
    def push(self):
        dx, dy, dz = self.distance
        x, y, z = self.transform.position
        a, b, c = self.orientation
        
        glPushMatrix()
        glTranslatef(-dx, -dy, -dz)
        glRotatef(-a, 1, 0, 0)
        glRotatef(-b, 0, 1, 0)
        glRotatef(c, 0, 0, 1)
        glTranslatef(-x, -y, z)
    def pop(self):
        glPopMatrix()
    def set_facing_matrix(self):
        a, b, c = self.orientation
        glRotatef(-a, 0, 0, 1)
        glRotatef(b, 0, 1, 0)
        glRotatef(c, 1, 0, 0)
    def set_skybox_data(self):
        a, b, c = self.orientation
        glRotatef(-a, 1, 0, 0)
        glRotatef(-b, 0, 1, 0)
        glRotatef(c, 0, 0, 1)


class Light(Component):
    _gllights = range(GL_LIGHT0, GL_LIGHT7 + 1) # Max 8 lights
    def __init__(self, ambient=(0, 0, 0, 1), diffuse=(1, 1, 1, 1),
                 specular=(1, 1, 1, 1), spot_direction=(0, 0, 1)):
        Component.__init__(self)
        self.gl_light = Light._getnextlight()
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.spot_direction = spot_direction + (0,)
        self.directional = False
    def enable(self):
        if self.gl_light is not None:
            gl_light = self.gl_light
            x, y, z = self.transform.position
            glposition = (x, y, -z, int(not self.directional))
            glLightfv(gl_light, GL_AMBIENT, self.ambient)
            glLightfv(gl_light, GL_DIFFUSE, self.diffuse)
            glLightfv(gl_light, GL_SPECULAR, self.specular)
            glLightfv(gl_light, GL_SPOT_DIRECTION, self.spot_direction)
            glLightfv(gl_light, GL_POSITION, glposition)
            glEnable(gl_light)
    def disable(self):
        if self.gl_light is not None:
            glDisable(self.gl_light)
    @classmethod
    def _getnextlight(cls):
        try: return cls._gllights.pop()
        except IndexError: return None



# ==============================
# GameObject & Primitives
# ==============================

class GameObject(object):
    
    _camera = None
    _lights = []
    
    def __init__(self, transform=Transform(), *components):
        self.parent = None
        self.children = []
        self.name = ''
        self.tag = ''
        self.transform = None
        self.rigidbody = None
        self.collider = None
        self.renderables = []
        self.components = []
        self.addcomponent(transform)
        for c in components: self.addcomponent(c)
        
    def getcomponentbyclass(self, cls):
        for c in self.components:
            if isinstance(c, cls):
                return c
    
    def addcomponents(self, *components):
        for component in components:
            self.addcomponent(component)

    def addcomponent(self, component):
        if isinstance(component, Camera):
            GameObject._camera = component
        self._updatecomponents('append', component)
        self._checkfield('transform', component)
        self._checkfield('rigidbody', component)
        self._checkfield('collider', component)
        component.gameobject = self
        component.start()
        
    def removecomponent(self, component):
        if component is None: return
        if isinstance(component, Camera):
            GameObject._camera = None
        self._updatecomponents('remove', component)
        Component.__init__(component)

    def _checkfield(self, clsstring, component): # Use with caution!
        if isinstance(component, eval(clsstring.capitalize())):
            oldcomponent = self.__dict__[clsstring]
            self.__dict__[clsstring] = component
            self.removecomponent(oldcomponent)
            
    def _updatecomponents(self, action, component):
        if isinstance(component, Light):
            getattr(GameObject._lights, action)(component)
        if isinstance(component, Component):
            getattr(self.components, action)(component)
        if isinstance(component, Renderer):
            getattr(self.renderables, action)(component)
            
    def handlemessage(self, string, data=None):
        for component in self.components:
            result = component.handlemessage(string, data)
            if result is not None: return result

    def update(self):
        for component in self.components: component.update()
        for gameobject in self.children: gameobject.update()

    def render(self):
        for component in self.renderables: component.render()
        for gameobject in self.children: gameobject.render()

    def oncollision(self, other):
        for component in self.components: component.oncollision(other)

    def destroy(self):
        self.parent.removegameobject(self)

    def addgameobjects(self, *gameobjects):
        for gameobject in gameobjects:
            self._addgameobject(gameobject)

    def addgameobject(self, gameobject):
        self._addgameobject(gameobject)

    def _addgameobject(self, gameobject):
        self.children.append(gameobject)
        gameobject.parent = self

    def removegameobject(self, gameobject):
        self.children.remove(gameobject)
        gameobject.parent = None


class CubePrimitive(GameObject):
    def __init__(self, transform, color, density=10):
        GameObject.__init__(self, transform, Rigidbody(density),
                            Cube(color), BoxCollider())


class SpherePrimitive(GameObject):
    def __init__(self, transform, color, density=10):
        GameObject.__init__(self, transform, Rigidbody(density),
                            Sphere(color), SphereCollider())



# ==============================
# Color
# ==============================

class MetaColor(type):
    @property
    def red(cls): return cls(1, 0, 0, 1)  # @NoSelf
    @property
    def green(cls): return cls(0, 1, 0, 1)  # @NoSelf
    @property
    def blue(cls): return cls(0, 0, 1, 1)  # @NoSelf
    @property
    def yellow(cls): return cls(1, 1, 0, 1)  # @NoSelf
    @property
    def magenta(cls): return cls(1, 0, 1, 1)  # @NoSelf
    @property
    def cyan(cls): return cls(0, 1, 1, 1)  # @NoSelf
    @property
    def black(cls): return cls(0, 0, 0, 1)  # @NoSelf
    @property
    def white(cls): return cls(1, 1, 1, 1)  # @NoSelf
    @property
    def gray(cls): return cls(.5, .5, .5, 1)  # @NoSelf


class Color(object):
    __metaclass__ = MetaColor
    def __init__(self, r=0, g=0, b=0, a=1):
        self.__color = (r, g, b, a)
    def __getitem__(self, index):
        return self.__color[index]
    def __repr__(self):
        return self.__color



# ==============================
# Game
# ==============================

class RenderCore(object):
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
        comppath = os.path.join(*path)
        icon = pygame.image.load(comppath).convert_alpha()
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
        glClearColor(*Color.gray)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glFrontFace(GL_CCW)
        glCullFace(GL_BACK)
    @classmethod
    def flip(cls):
        pygame.display.flip()
    @classmethod
    def quit(cls):
        pygame.quit()


class Scene(GameObject):
    def __init__(self, gravity=(0, -9.8, 0), erp=.8, cfm=1e-5):
        GameObject.__init__(self, Transform())
        PhysicsEngine.start(gravity, erp, cfm)


class Game(object):
    
    def __init__(self, screensize=(800, 600),
                 title="Pyngine game", hwsurface=False):
        self.screensize = screensize
        self.title = title
        self.camera = None
        self.lights = []
        self.scene = Scene()
        RenderCore.init(screensize, hwsurface)
        RenderCore.setwindowtitle(title)
        RenderCore.setwindowicon(['..', '..', 'icon.png'])
        RenderCore.dostuff()
        RenderCore.enable()
        
    def mainloop(self, fps=60):
        try:
            self._mainloop(fps)
        except Error as e:
            print "Oops! %s: %s" % (e.errno, e.strerror)
        finally:
            RenderCore.quit()
            
    def _mainloop(self, fps):
        step = 1. / fps
        clock = pygame.time.Clock()
        while not Input.quitflag:
            Input.update()
            self.scene.update()
            self._renderloop()
            PhysicsEngine.collide()
            PhysicsEngine.step(step)
            clock.tick(fps)
            
    def _renderloop(self):
        RenderCore.setviewport()
        RenderCore.setperspective()
        RenderCore.initmodelviewmatrix()
        RenderCore.clearscreen()
        if GameObject._camera: GameObject._camera.push()
        for light in GameObject._lights: light.enable()
        self.scene.render()
        if GameObject._camera: GameObject._camera.pop()
        RenderCore.flip()
