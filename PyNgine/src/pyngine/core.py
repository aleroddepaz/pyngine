import ode
import pygame
import pygame.locals as pgl
from itertools import imap
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


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
        self.body.setPosition(self.gameobject.transform.position)
    def update(self):
        self.gameobject.transform.position = self.body.getPosition()
        self.gameobject.transform.rotation = self.body.getQuaternion()[:3]
    def addforce(self, force):
        self.body.addForce(force)
    def oncollision(self):
        pass


class Transform(Component):
    def __init__(self, position=(0,0,0), rotation=(0,0,0), scale=(1,1,1)):
        Component.__init__(self)
        self.position = position
        self.rotation = rotation
        self.scale = scale
        self.right = (1,0,0)
        self.up = (0,1,0)
        self.forward = (0,0,1)
    def move(self, position):
        x1, y1, z1 = self.position
        x2, y2, z2 = position
        self.position = (x1+x2, y1+y2, z1+z2)
    def rotate(self, rotation):
        a1, b1, c1 = self.rotation
        a2, b2, c2 = rotation
        self.rotation = (a1+a2, b1+b2, c1+c2)
    def rotatearound(self, other):
        pass # TO DO
    def lookat(self, other):
        pass # TO DO


class Camera(Renderer):
    def __init__(self, distance=(0,0,0)):
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
    gl_lights = range(GL_LIGHT0, GL_LIGHT7+1)
    def __init__(self, ambient=(0,0,0,1),diffuse=(1,1,1,1),
                 specular=(1,1,1,1),spot_direction=(0,0,1)):
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
            glLightfv(self.gl_light, GL_SPOT_DIRECTION, self.spot_direction+(0,))
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
    def __init__(self, color=(0,0,0,1),
                 mirror=True, hide_faces=[]):
        Renderer.__init__(self)
        self.hide_faces = hide_faces
        self.size = 1
        self.color = color
        self.mirror = mirror
        self.corners = ((-1, -1, 1),#topleftfront
                      (1, -1, 1),#toprightfront
                      (1, 1, 1),#bottomrightfront
                      (-1, 1, 1),#bottomleftfront
                      (-1, -1, -1),#topleftback
                      (1, -1, -1),#toprightback
                      (1, 1, -1),#bottomrightback
                      (-1, 1, -1))#bottomleftback

        sides = ((7,4,0,3, 2, 2, 5),#left
                      (2,1,5,6, 3, 4, 4),#right
                      (7,3,2,6, 5, 0, 3),#top
                      (0,4,5,1, 4, 5, 2),#bottom
                      (3,0,1,2, 0, 1, 0),#front
                      (6,5,4,7, 1, 3, 1))#back
        self.sides = []
        if not "left" in hide_faces:
            self.sides.append(sides[0])
        if not "right" in hide_faces:
            self.sides.append(sides[1])
        if not "top" in hide_faces:
            self.sides.append(sides[2])
        if not "bottom" in hide_faces:
            self.sides.append(sides[3])
        if not "front" in hide_faces:
            self.sides.append(sides[4])
        if not "back" in hide_faces:
            self.sides.append(sides[5])
        self.normals = ((0, 0, 1), #front
                        (0, 0, -1), #back
                        (0, -1, 0), #top
                        (0, 1, 0), #bottom
                        (1, 0, 0), #right
                        (-1, 0, 0)) #left
        self.split_coords = ((2,2),#top
                             (0,1),#back
                             (1,1),#left
                             (2,1),#front
                             (3,1),#right
                             (2,0))#bottom
        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)
        ox = .25
        oy = .33
        for i in self.sides:
            ix = 0
            x, y = self.split_coords[i[5]]
            x *= ox
            y *= oy
            if self.mirror: coords = ((1,1), (1,0), (0,0), (0,1))
            else: coords = ((x+ox, y+oy), (x+ox, y), (x, y), (x, y+oy))
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
        glScalef(.5, .5, .5)
        try:
            if self.transform.scale != (1, 1, 1):
                glScalef(*self.transform.scale)
        except: pass
        glColor(*self.color)
        glCallList(self.gl_list)
        glPopMatrix()


class CubeCollider(Collider):
    def __init__(self, world, size=(1,1,1), density=1):
        Collider.__init__(self, world)
        self.size = size
        mass = ode.Mass()
        mass.setBox(density, *size)
        self.body.setMass(mass)


class GameObject(object):
    def __init__(self, transform=Transform(), *components):
        self.transform = transform
        self.rigidbody = None
        self.components = []
        self.renderables = []
        self.tag = ''
        for c in components:
            if c!=None: self.addcomponent(c)
        
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


class CubePrimitive(GameObject):
    def __init__(self, transform, color, world, density=1):
        GameObject.__init__(self, transform)
        self.addcomponent(Cube(color))
        self.addcomponent(CubeCollider(world, transform.scale, density))


class Game(object):
    def __init__(self, screen_size=(800, 600), title="PyNgine Game"):
        self.screen_size = screen_size
        self.title = title
        self.camera = None
        self.lights = []
        self.gameobjects = []
        self.world = ode.World()

        pygame.init()
        screen_size = self.screen_size
        pygame.display.set_caption(title)
        # pygame.display.set_icon(icono)
        params = pgl.OPENGL | pgl.DOUBLEBUF
        # params |= FULLSCREEN
        # params |= HWSURFACE
        # params |= NOFRAME
        pygame.display.set_mode(screen_size, params)
        
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE);
        glEnable(GL_LIGHTING)
        glEnable(GL_NORMALIZE)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glEnable(GL_SCISSOR_TEST)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)
        glPointSize(10)
        self.clear_screen()
        glFogfv(GL_FOG_COLOR, (.5,.5,.5,.5))
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogf(GL_FOG_DENSITY, .35)
        glHint(GL_FOG_HINT, GL_NICEST)
        glFogf(GL_FOG_START, 10.0)
        glFogf(GL_FOG_END, 125.0)
        glEnable(GL_FOG)
        glAlphaFunc(GL_GEQUAL, .5)
        glClearColor(0,0,0,0)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glFrontFace(GL_CCW)
        glCullFace(GL_BACK)
        glEnable(GL_CULL_FACE)
        
    def addgameobject(self, gameobject):
        self.gameobjects.append(gameobject)
        for c in gameobject.components:
            if isinstance(c, Camera):
                self.camera = c
            if isinstance(c, Light):
                self.lights.append(c)

    def renderloop(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glViewport(0,0,*self.screen_size)
        view_angle = 45
        close_view = 0.1
        far_view = 100.0
        gluPerspective(view_angle, 1.0*self.screen_size[0]/self.screen_size[1], close_view, far_view)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glEnable(GL_DEPTH_TEST)

        self.clear_screen()
        if self.camera: self.camera.push()
        for light in self.lights: light.enable()
        glEnable(GL_ALPHA_TEST)
        for gameobject in self.gameobjects:
            gameobject.render()
        glDisable(GL_ALPHA_TEST)
        if self.camera: self.camera.pop()
        pygame.display.flip()
        
    def clear_screen(self):
        glDisable(GL_SCISSOR_TEST)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
        glEnable(GL_SCISSOR_TEST)

    def mainloop(self, fps=60):
        try:
            self.__mainloop(fps)
        except Error as e:
            print "Oops! {0}: {1}".format(e.errno, e.strerror)
        finally:
            pygame.quit()

    def __mainloop(self, fps):
        step = 1./fps
        clock = pygame.time.Clock()
        while not Input.quitflag:
            newtitle = "%s - FPS: %s" % (self.title, clock.get_fps())
            pygame.display.set_caption(newtitle)
            Input.update()
            for gameobject in self.gameobjects:
                gameobject.update()
            self.renderloop()
            self.world.step(step)
            clock.tick(fps)


class Input(object):
    quitflag = False
    keys = {}
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
        except:
            cls.keys[key] = False
            return False


### ========== Example ==========

class ExampleComponent(Component):
    def update(self):
        self.transform.rotate((0, 0.5, 0))

class ExampleMoveComponent(Component):
    def start(self):
        self.speed = 0.1
    def update(self):
        speed = self.speed
        if Input.getkey(pgl.K_z): speed *= 2
        if Input.getkey(pgl.K_UP): self.transform.move((0,0,speed))
        if Input.getkey(pgl.K_DOWN): self.transform.move((0,0,-speed))
        if Input.getkey(pgl.K_RIGHT): self.transform.move((speed,0,0))
        if Input.getkey(pgl.K_LEFT): self.transform.move((-speed,0,0))
        if Input.getkey(pgl.K_w): self.transform.move((0,speed,0))
        if Input.getkey(pgl.K_s): self.transform.move((0,-speed,0))

class ExampleGame(Game):
    def __init__(self):
        Game.__init__(self)
        #self.world.setGravity((0,-10,0))
        
        cameraobj = GameObject()
        cameraobj.addcomponent(Camera((0,0,10)))
        cameraobj.addcomponent(ExampleMoveComponent())
        
        lightobj = GameObject(Transform((0,10,0)))
        lightobj.addcomponent(Light())
        
        t1 = Transform(position=(0,0,0), scale=(2,2,2))
        cubeobj1 = CubePrimitive(transform=t1, color=(1,0,0,1), world = self.world)
        
        cubeobj2 = CubePrimitive(Transform((0,2,2)), (0,0,1,1), self.world)
        cubeobj2.addcomponent(ExampleComponent())
        
        cubeobj3 = GameObject(Transform((0,-2,-5)), CubeCollider(self.world))
        cubeobj3.addcomponent(Cube(color=(0,1,0,1)))
        cubeobj3.rigidbody.addforce((0,50,0))
        
        cubeobj4 = GameObject(Transform((0,5,-5)), CubeCollider(self.world))
        cubeobj4.addcomponent(Cube(color=(0.5,0.5,0,1)))
        cubeobj4.rigidbody.addforce((0,-50,0))
        
        self.addgameobject(cameraobj)
        self.addgameobject(lightobj)
        self.addgameobject(cubeobj1)
        self.addgameobject(cubeobj2)
        self.addgameobject(cubeobj3)
        self.addgameobject(cubeobj4)

game = ExampleGame()
game.mainloop()
