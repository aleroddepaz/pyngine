import ode
import pygame
import pygame.locals as pgl
from itertools import imap
from OpenGL.GL import *  # @UnusedWildImport
from OpenGL.GLU import *  # @UnusedWildImport
from OpenGL.GLUT import *  # @UnusedWildImport



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
    def __init__(self):
        Component.__init__(self)
    def render(self):
        pass


class Collider(Component):
    def __init__(self, world):
        Component.__init__(self)
        self.body = ode.Body(world)
    def start(self):
        self.setposition(self.gameobject.transform.position)
    def update(self):
        self.gameobject.transform.position = self.body.getPosition()
        self.gameobject.transform.rotation = self.body.getQuaternion()[:3]
    def addforce(self, force):
        self.body.addForce(force)
    def setposition(self, position):
        self.body.setPosition(position)
    def oncollision(self):
        pass


class Transform(Component):
    def __init__(self, position=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
        Component.__init__(self)
        self.position = position
        self.rotation = rotation
        self.scale = scale
        self.right = (1, 0, 0)
        self.up = (0, 1, 0)
        self.forward = (0, 0, 1)
    def move(self, position):
        self.position = map(sum, zip(self.position, position))
    def rotate(self, rotation):
        self.rotation = map(sum, zip(self.rotation, rotation))
    def rotatearound(self, other):
        pass  # TO DO
    def lookat(self, other):
        pass  # TO DO


class Camera(Renderer):
    def __init__(self, distance=(0, 0, 0)):
        Renderer.__init__(self)
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
    gl_lights = range(GL_LIGHT0, GL_LIGHT7 + 1) # Max 8 lights
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
        try: return cls.gl_lights.pop()
        except IndexError: return None


class Cube(Renderer):
    def __init__(self, color=(0, 0, 0, 1)):
        Renderer.__init__(self)
        self.color = color
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
        self.gl_list = glGenLists(1)
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

    def render(self):
        x, y, z = self.transform.position
        a, b, c = self.transform.rotation
        glPushMatrix()
        glTranslatef(x, y, -z)
        glRotatef(a, 1, 0, 0)
        glRotatef(b, 0, 1, 0)
        glRotatef(c, 0, 0, 1)
        try:
            if self.transform.scale != (1, 1, 1):
                glScalef(*self.transform.scale)
        except: pass
        glColor(*self.color)
        glCallList(self.gl_list)
        glPopMatrix()


class CubeCollider(Collider):
    def __init__(self, world, size=(1, 1, 1), density=1):
        Collider.__init__(self, world)
        self.size = size
        mass = ode.Mass()
        mass.setBox(density, *size)
        self.body.setMass(mass)


# ==============================
# GameObject & Primitives
# ==============================

class GameObject(object):
    def __init__(self, transform=Transform(), *components):
        self.transform = transform
        self.rigidbody = None
        self.components = []
        self.renderables = []
        self.scene = None
        self.tag = ''
        for c in components:
            if c != None: self.addcomponent(c)
        
    def addcomponent(self, component):
        self.__updatecomponents('append', component)
        self.__checktransformcomponent(component)
        self.__checkrigidbodycomponent(component)
        component.gameobject = self
        component.transform = self.transform
        component.start()
        
    def removecomponent(self, component):
        self.__updatecomponents('remove', component)
        component.gameobject = None
        component.transform = None
        
    def getcomponentsbyclass(self, cls):
        return filter(lambda c: isinstance(c, cls), self.components)
    
    def setposition(self, newposition):
        self.transform.position = newposition
        self.rigidbody.setposition(newposition)
            
    def __checktransformcomponent(self, component):
        if isinstance(component, Transform):
            oldtransform = self.transform
            self.transform = component
            for c in self.components:
                c.transform = component
            self.removecomponent(oldtransform)
            
    def __checkrigidbodycomponent(self, component):
        if isinstance(component, Collider):
            if self.rigidbody != None:
                oldrigidbody = self.rigidbody
                self.rigidbody = component
                self.removecomponent(oldrigidbody)
            else: self.rigidbody = component
            
    def __updatecomponents(self, action, component):
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
    def render(self):
        for component in self.renderables: component.render()
    def destroy(self):
        self.scene.removegameobject(self)


class CubePrimitive(GameObject):
    def __init__(self, transform, color, world, density=1):
        GameObject.__init__(self, transform)
        self.addcomponent(Cube(color))
        self.addcomponent(CubeCollider(world, transform.scale, density))


# ==============================
# Game
# ==============================

class Game(object):
    def __init__(self, screensize=(800, 600), title="Pyngine game"):
        self.screensize = screensize
        self.title = title
        self.camera = None
        self.lights = []
        self.gameobjects = []
        self.world = ode.World()

        pygame.init()
        pygame.display.set_caption(title)
        Input.setmousevisibility(False)
        params = pgl.OPENGL | pgl.DOUBLEBUF
        # params |= pgl.HWSURFACE
        pygame.display.set_mode(self.screensize, params)
        path = os.path.join('..', '..', 'icon.png')
        icon = pygame.image.load(path).convert_alpha()
        pygame.display.set_icon(icon)
        
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
        glShadeModel(GL_SMOOTH)
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glPointSize(10)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
        glFogfv(GL_FOG_COLOR, (.5, .5, .5, .5))
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogf(GL_FOG_DENSITY, .35)
        glHint(GL_FOG_HINT, GL_NICEST)
        glFogf(GL_FOG_START, 10.0)
        glFogf(GL_FOG_END, 125.0)
        glAlphaFunc(GL_GEQUAL, .5)
        glClearColor(0, 0, 0, 0)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glFrontFace(GL_CCW)
        glCullFace(GL_BACK)
        # Enabling stuff
        glEnable(GL_FOG)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)
        glEnable(GL_NORMALIZE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glEnable(GL_SCISSOR_TEST)
        glEnable(GL_CULL_FACE)
        
    def addgameobject(self, gameobject):
        self.__addgameobject(gameobject)
    def addgameobjects(self, *gameobjects):
        for gameobject in gameobjects:
            self.__addgameobject(gameobject)
    def removegameobject(self, gameobject):
        self.gameobjects.remove(gameobject)
        gameobject.scene = None

    def renderloop(self):
        # Viewport
        glViewport(0, 0, *self.screensize)
        # Projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        view_angle = 45
        close_view = 0.1
        far_view = 100.0
        gluPerspective(view_angle, 1.0 * self.screensize[0] / self.screensize[1], close_view, far_view)
        # Initialize ModelView matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # Clear screen
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
        
        if self.camera: self.camera.push()
        for light in self.lights: light.enable()
        glEnable(GL_ALPHA_TEST)
        for gameobject in self.gameobjects:
            gameobject.render()
        glDisable(GL_ALPHA_TEST)
        if self.camera: self.camera.pop()
        pygame.display.flip()

    def mainloop(self, fps=60):
        try: self.__mainloop(fps)
        except Error as e: print "Oops! %s: %s" % (e.errno, e.strerror)
        finally: pygame.quit()

    def __addgameobject(self, gameobject):
        self.gameobjects.append(gameobject)
        gameobject.scene = self
        for c in gameobject.components:
            if isinstance(c, Camera):
                self.camera = c
            if isinstance(c, Light):
                self.lights.append(c)

    def __mainloop(self, fps):
        step = 1. / fps
        clock = pygame.time.Clock()
        while not Input.quitflag:
            Input.update()
            for gameobject in self.gameobjects:
                gameobject.update()
            self.renderloop()
            self.world.step(step)
            clock.tick(fps)


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

class Color(object):
    __metaclass__ = MetaColor
    def __init__(self, r=0, g=0, b=0, a=1):
        self.__color = (r, g, b, a)
    def __getitem__(self, index):
        return self.__color[index]


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
        
        cameraobj = GameObject()
        cameraobj.addcomponent(Camera((0, 0, 10)))
        cameraobj.addcomponent(ExampleMoveComponent())
        
        lightobj1 = GameObject(Transform((0, 7, 0)))
        lightobj1.addcomponent(Light())
        
        lightobj2 = GameObject(Transform((7, 0, 0)))
        lightobj2.addcomponent(Light())
        
        t1 = Transform(position=(0, 0, 0), scale=(2, 2, 2))
        cubeobj1 = CubePrimitive(transform=t1, color=Color.red, world=self.world)
        cubeobj1.addcomponent(ExampleScaleComponent())
        
        cubeobj2 = CubePrimitive(Transform((0, 2, 2)), Color.green, self.world)
        cubeobj2.addcomponent(ExampleComponent())
        
        cubeobj3 = CubePrimitive(Transform((0, -5, -5)), Color.blue, self.world)
        cubeobj3.addcomponent(ExampleComponent())
        cubeobj3.rigidbody.addforce((0, 50, 0))
        
        cubeobj4 = CubePrimitive(Transform((0, 2, -5)), Color.yellow, self.world)
        cubeobj4.addcomponent(ExampleComponent())
        cubeobj4.rigidbody.addforce((0, -50, 0))
        
        self.addgameobjects(cameraobj, lightobj1, lightobj2)
        self.addgameobjects(cubeobj1, cubeobj2, cubeobj3, cubeobj4)

game = ExampleGame()
game.mainloop()
