import os
import ode
import math
import pygame
import pygame.locals as pgl
from itertools import imap
from OpenGL.GL import *  # @UnusedWildImport
from OpenGL.GLU import *  # @UnusedWildImport


world = ode.World()


# ==============================
# Component & Subclasses
# ==============================

class Component(object):
    def __init__(self):
        self.gameobject = None
        self.transform = None
    def start(self):
        pass
    def update(self):
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
        a, b, c = self.transform.rotation
        glPushMatrix()
        glTranslatef(x, y, -z)
        glRotatef(a, 1, 0, 0)
        glRotatef(b, 0, 1, 0)
        glRotatef(c, 0, 0, 1)
        if self.transform.scale != (1, 1, 1):
            glScalef(*self.transform.scale)
        glColor(*self.color)
        glCallList(self.gl_list)
        glPopMatrix()
    def calculatenormal(self, p1, p2, p3):
        v1 = (p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2])
        v2 = (p3[0]-p1[0], p3[1]-p1[1], p3[2]-p1[2])
        vx = (v1[1] * v2[2]) - (v1[2] * v2[1])
        vy = (v1[2] * v2[0]) - (v1[0] * v2[2])
        vz = (v1[0] * v2[1]) - (v1[1] * v2[0])
        return (vx, vy, vz)


class Rigidbody(Component):
    def __init__(self):
        Component.__init__(self)
    def addforce(self, force):
        self.transform.body.addForce(force)
    def oncollision(self):
        pass


class Transform(Component):
    def __init__(self, position=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
        Component.__init__(self)
        self.body = ode.Body(world)
        self.position = position
        self.rotation = rotation
        self._scale = scale
        self.right = (1, 0, 0)
        self.up = (0, 1, 0)
        self.forward = (0, 0, 1)
    @property
    def position(self):
        return self.body.getPosition()
    @position.setter
    def position(self, value):
        self.body.setPosition(value)
    @property
    def rotation(self):
        return self._rotation
    @rotation.setter
    def rotation(self, value):
        self._rotation = value
    @property
    def scale(self):
        return self._scale
    @scale.setter
    def scale(self, value):
        self._scale = value
    def move(self, position):
        self.position = map(sum, zip(self.position, position))
    def rotate(self, rotation):
        self.rotation = map(sum, zip(self.rotation, rotation))
    def rotatearound(self, other):
        pass  # TO DO
    def lookat(self, other):
        pass  # TO DO


class Camera(Component):
    def __init__(self, distance=(0, 0, 0)):
        Component.__init__(self)
        self.distance = distance
    def push(self):
        dx, dy, dz = self.distance
        x, y, z = self.transform.position
        a, b, c = self.transform.rotation
        glPushMatrix()
        glTranslatef(-dx, -dy, -dz)
        glRotatef(-a, 1, 0, 0)
        glRotatef(-b, 0, 1, 0)
        glRotatef(c, 0, 0, 1)
        glTranslatef(-x, -y, z)
    def pop(self):
        glPopMatrix()
    def set_facing_matrix(self):
        a, b, c = self.transform.rotation
        glRotatef(-a, 0, 0, 1)
        glRotatef(b, 0, 1, 0)
        glRotatef(c, 1, 0, 0)
    def set_skybox_data(self):
        a, b, c = self.transform.rotation
        glRotatef(-a, 1, 0, 0)
        glRotatef(-b, 0, 1, 0)
        glRotatef(c, 0, 0, 1)


class Light(Component):
    _gllights = range(GL_LIGHT0, GL_LIGHT7 + 1) # Max 8 lights
    def __init__(self, ambient=(0, 0, 0, 1), diffuse=(1, 1, 1, 1),
                 specular=(1, 1, 1, 1), spot_direction=(0, 0, 1)):
        Component.__init__(self)
        self.gl_light = Light.__getnextlight()
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.spot_direction = spot_direction
        self.directional = False
    def enable(self):
        if self.gl_light != None:
            x, y, z = self.transform.position
            glLightfv(self.gl_light, GL_AMBIENT, self.ambient)
            glLightfv(self.gl_light, GL_DIFFUSE, self.diffuse)
            glLightfv(self.gl_light, GL_SPECULAR, self.specular)
            glLightfv(self.gl_light, GL_SPOT_DIRECTION, self.spot_direction + (0,))
            glLightfv(self.gl_light, GL_POSITION, (x, y, -z, int(not self.directional)))
            glEnable(self.gl_light)
    def disable(self):
        if self.gl_light != None:
            glDisable(self.gl_light)
    @classmethod
    def __getnextlight(cls):
        try: return cls._gllights.pop()
        except IndexError: return None


class Sphere(Renderer):
    def __init__(self, color=(0, 0, 0, 1)):
        Renderer.__init__(self, color)
        glNewList(self.gl_list, GL_COMPILE)
        
        verts = []
        texcs = []
        norms = []
        space = 15 #self.detail
        for meridian in xrange(0, 180, space):
            for parallels in xrange(0, 360, space):
                _v = []
                _t = []
                for i in xrange(2):
                    for j in xrange(2):
                        phi = (parallels + space*i) / 180.
                        theta = (meridian + space*j) / 180.
                        x = math.sin(phi*math.pi) * math.sin(theta*math.pi) * 0.5
                        z = math.cos(phi*math.pi) * math.sin(theta*math.pi) * 0.5
                        y = math.cos(theta*math.pi) * 0.5
                        _v.append((x,y,z))
                        _t.append((phi/2, 1 - theta))
                verts.extend([_v[0], _v[1], _v[3], _v[0], _v[3], _v[2]])
                texcs.extend([_t[0], _t[1], _t[3], _t[0], _t[3], _t[2]])
                norms.extend([self.calculatenormal(*verts[-6:-3])]*3)
                norms.extend([self.calculatenormal(*verts[-3::])]*3)
        glBegin(GL_TRIANGLES)
        for i, vert in enumerate(verts):
            u,v = texcs[i]
            glTexCoord2f(u,v)
            glNormal3f(*norms[i])
            glVertex3f(*vert)
        glEnd()
        glEndList()

class Cube(Renderer):
    def __init__(self, color=(0, 0, 0, 1)):
        Renderer.__init__(self, color)
        self.corners = [(-0.5, -0.5, 0.5),
                      (0.5, -0.5, 0.5),  # toprightfront
                      (0.5, 0.5, 0.5),  # bottomrightfront
                      (-0.5, 0.5, 0.5),  # bottomleftfront
                      (-0.5, -0.5, -0.5),  # topleftback
                      (0.5, -0.5, -0.5),  # toprightback
                      (0.5, 0.5, -0.5),  # bottomrightback
                      (-0.5, 0.5, -0.5)]  # bottomleftback
        self.sides = [(7, 4, 0, 3, 2, 2, 5),  # left
                      (2, 1, 5, 6, 3, 4, 4),  # right
                      (7, 3, 2, 6, 5, 0, 3),  # top
                      (0, 4, 5, 1, 4, 5, 2),  # bottom
                      (3, 0, 1, 2, 0, 1, 0),  # front
                      (6, 5, 4, 7, 1, 3, 1)]  # back
        self.normals = ((0, 0, 1),  # front
                        (0, 0, -1),  # back
                        (0, -1, 0),  # top
                        (0, 1, 0),  # bottom
                        (1, 0, 0),  # right
                        (-1, 0, 0))  # left
        self.split_coords = ((2, 2),  # top
                             (0, 1),  # back
                             (1, 1),  # left
                             (2, 1),  # front
                             (3, 1),  # right
                             (2, 0))  # bottom
        coords = ((1,1), (1,0), (0,0), (0,1))
        glNewList(self.gl_list, GL_COMPILE)
        for i in self.sides:
            ix = 0
            x, _ = self.split_coords[i[5]]
            glBegin(GL_QUADS)
            glNormal3f(*self.normals[i[6]])
            for x in i[:4]:
                glTexCoord2fv(coords[ix])
                a, b, c = self.corners[x]
                glVertex3f(a,b,c)
                ix += 1
            glEnd()
        glEndList()



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
        
        self.transform = transform
        self.rigidbody = None
        self.components = []
        self.renderables = []
        for c in components:
            if c != None: self.addcomponent(c)

    def addcomponent(self, component):
        if isinstance(component, Camera):
            GameObject._camera = component
        
        self._updatecomponents('append', component)
        self._checkcomponent('transform', component)
        self._checkcomponent('rigidbody', component)
        component.gameobject = self
        component.transform = self.transform
        component.start()
        
    def removecomponent(self, component):
        if component == None:
            return
        if isinstance(component, Camera):
            GameObject._camera = None
        
        self._updatecomponents('remove', component)
        component.gameobject = None
        component.transform = None
        
    def getcomponentbyclass(self, cls):
        for c in self.components:
            if isinstance(c, cls):
                return c
    
    def setposition(self, newposition):
        self.transform.position = newposition
        self.rigidbody.setposition(newposition)
            
    def _checkcomponent(self, clsstring, component): # Use with caution!
        if isinstance(component, eval(clsstring.capitalize())):
            oldcomponent = self.__dict__[clsstring]
            self.__dict__[clsstring] = component
            for c in self.components:
                c.__dict__[clsstring] = component
            self.removecomponent(oldcomponent)
            
    def _updatecomponents(self, action, component):
        if isinstance(component, Light):
            getattr(GameObject._lights, action)(component)
        if isinstance(component, Component):
            getattr(self.components, action)(component)
        if isinstance(component, Renderer):
            getattr(self.renderables, action)(component)
            
    def handlemessage(self, string, data=None):
        gen = imap(lambda x: x.handlemessage(string, data), self.components)
        for result in gen:
            if result != None: return result
    def update(self):
        for component in self.components: component.update()
        for gameobject in self.children: gameobject.update()
    def render(self):
        for component in self.renderables: component.render()
        for gameobject in self.children: gameobject.render()
    def destroy(self):
        self.parent.removegameobject(self)
    
    def addgameobject(self, gameobject):
        self._addgameobject(gameobject)
    def addgameobjects(self, *gameobjects):
        for gameobject in gameobjects:
            self._addgameobject(gameobject)
    def _addgameobject(self, gameobject):
        self.children.append(gameobject)
        gameobject.parent = self
    def removegameobject(self, gameobject):
        self.children.remove(gameobject)
        gameobject.parent = None

class CubePrimitive(GameObject):
    def __init__(self, transform, color, density=1):
        GameObject.__init__(self, transform)
        self.addcomponent(Cube(color))
        self.addcomponent(Rigidbody())


class SpherePrimitive(GameObject):
    def __init__(self, transform, color, density=1):
        GameObject.__init__(self, transform)
        self.addcomponent(Sphere(color))
        self.addcomponent(Rigidbody())



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
    """
    Class implemented using the Facade pattern for
    abstracting the use of Pygame and OpenGL functions
    """
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
        params = pgl.OPENGL | pgl.DOUBLEBUF
        if hwsurface:
            params |= pgl.HWSURFACE
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
        gluPerspective(cls._viewangle, cls._aspect, cls._closeview, cls._farview)
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
    pass


class Game(object):
    def __init__(self, screensize=(800, 600), title="Pyngine game", hwsurface=False):
        self.screensize = screensize
        self.title = title
        self.camera = None
        self.lights = []
        self._root = GameObject()
        RenderCore.init(screensize, hwsurface)
        RenderCore.setwindowtitle(title)
        RenderCore.setwindowicon(['..', '..', 'icon.png'])
        RenderCore.dostuff()
        RenderCore.enable()
    
    # ===== Mainloop =====
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
            self._root.update()
            self._renderloop()
            world.step(step)
            clock.tick(fps)
    def _renderloop(self):
        RenderCore.setviewport()
        RenderCore.setperspective()
        RenderCore.initmodelviewmatrix()
        RenderCore.clearscreen()
        
        if GameObject._camera: GameObject._camera.push()
        for light in GameObject._lights: light.enable()
        glEnable(GL_ALPHA_TEST)
        self._root.render()
        glDisable(GL_ALPHA_TEST)
        if GameObject._camera: GameObject._camera.pop()
        RenderCore.flip()



# ==============================
# Input
# ==============================

class Input(object):
    quitflag = False
    keys = {}
    mousevisibility = True
    @classmethod
    def update(cls):
        for event in pygame.event.get():
            if event.type == pgl.QUIT:
                cls.quitflag = True
            if event.type == pgl.KEYUP:
                cls.keys[event.key] = False
            if event.type == pgl.KEYDOWN:
                cls.keys[event.key] = True
    @classmethod
    def getkey(cls, key):
        try:
            return cls.keys[key]
        except KeyError:
            cls.keys[key] = False
            return False
    @classmethod
    def getmouseposition(cls):
        return pygame.mouse.get_pos()
    @classmethod
    def getmousebutton(cls, index):
        return pygame.mouse.get_pressed()[index]
    @classmethod
    def getmousevisibility(cls):
        return cls.mousevisibility
    @classmethod
    def setmousevisibility(cls, boolean):
        cls.mousevisibility = boolean
        pygame.mouse.set_visible(boolean)



# ==============================
# Example
# ==============================

class ExampleComponent(Component):
    def update(self):
        self.transform.rotate((0, 0.5, 0))

class ExampleScaleComponent(Component):
    def start(self):
        self.scalefactor = .98
    def update(self):
        self.transform.scale = map(lambda x: x*self.scalefactor, self.transform.scale)
        if self.transform.scale[0] < 0.05: self.gameobject.destroy()

class ExampleMoveComponent(Component):
    def start(self):
        self.speed = 0.1
    def update(self):
        speed = self.speed
        if Input.getkey(pgl.K_z): speed *= 2
        if Input.getkey(pgl.K_UP): self.transform.move((0, 0, speed))
        if Input.getkey(pgl.K_DOWN): self.transform.move((0, 0, -speed))
        if Input.getkey(pgl.K_RIGHT): self.transform.move((speed, 0, 0))
        if Input.getkey(pgl.K_LEFT): self.transform.move((-speed, 0, 0))
        if Input.getkey(pgl.K_w): self.transform.rotate((speed*5, 0, 0))
        if Input.getkey(pgl.K_s): self.transform.rotate((-speed*5, 0, 0))
        if Input.getkey(pgl.K_a): self.transform.rotate((0, speed*5, 0))
        if Input.getkey(pgl.K_d): self.transform.rotate((0, -speed*5, 0))
        
class ExampleGame(Game):
    def __init__(self):
        Game.__init__(self)
        scene = Scene()
        
        cameraobj = GameObject()
        cameraobj.addcomponent(Camera((0, 0, 10)))
        cameraobj.addcomponent(ExampleMoveComponent())
        lightobj1 = GameObject(Transform((0, 7, 0)))
        lightobj1.addcomponent(Light())
        lightobj2 = GameObject(Transform((7, 0, 0)))
        lightobj2.addcomponent(Light())
        scene.addgameobjects(cameraobj, lightobj1, lightobj2)

        t1 = Transform(position=(0, 0, 0), scale=(2, 2, 2))
        cubeobj1 = CubePrimitive(transform=t1, color=Color.red)
        cubeobj1.addcomponent(ExampleScaleComponent())
        
        cubeobj2 = CubePrimitive(Transform((0, 2, 2)), Color.green)
        cubeobj2.addcomponent(ExampleComponent())
        
        cubeobj3 = CubePrimitive(Transform((0, -5, -5)), Color.blue)
        cubeobj3.addcomponent(ExampleComponent())
        cubeobj3.rigidbody.addforce((0, 50, 0))
        
        cubeobj4 = SpherePrimitive(Transform((0, 2, -5)), Color.yellow)
        cubeobj4.addcomponent(ExampleComponent())
        cubeobj4.rigidbody.addforce((0, -50, 0))
        
        scene.addgameobjects(cubeobj1, cubeobj2, cubeobj3, cubeobj4)

        self._root = scene
        
        """
        cube = CubePrimitive(Transform((2, 0, 0)), Color.blue)
        sphere = SpherePrimitive(Transform((-2, 0, 0)), Color.yellow)
        self.addgameobjects(cube, sphere)
        """

game = ExampleGame()
game.mainloop()
