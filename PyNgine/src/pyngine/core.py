import pygame
from pygame.locals import *
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


class Renderer(Component):
    def __init__(self):
        Component.__init__(self)
    def render(self):
        pass


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
            if self.transform.scale != (1, 1, 1): glScalef(*self.transform.scale)
        except: pass
        glColor(*self.color)
        glCallList(self.gl_list)
        glPopMatrix()


class GameObject(object):
    def __init__(self, transform=Transform()):
        self.transform = transform
        self.components = [transform]
        self.renderables = []
        self.colliders = []
    def addcomponent(self, component):
        self.__updatecomponents('append', component)
        component.gameobject = self
        component.transform = self.transform
        component.start()
    def removecomponent(self, component):
        self.__updatecomponents('remove', component)
        component.gameobject = None
        component.transform = None
    def __updatecomponents(self, action, component):
        getattr(self.components, action)(component)
        if isinstance(component, Renderer):
            getattr(self.renderables, action)(component)
        if isinstance(component, Collider):
            getattr(self.colliders, action)(component)
    def handlemessage(self, string, data=None):
        result = None
        for component in self.components:
            result = component.handlemessage(string, data)
            if result != None: break
        return result
    def update(self):
        for component in self.components:
            component.update()
    def render(self):
        for component in self.renderables:
            component.render()


class Collider(Component):
    def __init__(self, fillcolor, strokecolor, strokewidth, alpha, zoom):
        self.fillcolor = fillcolor
        self.strokecolor = strokecolor
        self.strokewidth = strokewidth
        self.alpha = alpha
        self.zoom = zoom
    def render(self, x, y, angle, zoom):
        pass


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


class Game(object):
    def __init__(self, screen_size=(800, 600)):
        self.screen_size = screen_size
        self.camera = None
        self.lights = []
        self.gameobjects = []
        self.init()
    def init(self):
        pygame.init()
        screen_size = self.screen_size
        # pygame.display.set_caption(titulo)
        # pygame.display.set_icon(icono)
        params = OPENGL | DOUBLEBUF
        # params |= FULLSCREEN
        # params |= HWSURFACE
        # params |= NOFRAME
        pygame.display.set_mode(screen_size, params)
        
        ### start GL stuff
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
        ### end GL stuff
        
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

        for gameobject in self.gameobjects:
            gameobject.update()

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

    def mainloop(self):
        try:
            self.__mainloop()
        except:
            print("Oops!")
        finally:
            pygame.quit()

    def __mainloop(self):
        while not Input.quitflag:
            Input.update()
            self.renderloop()


class Input(object):
    quitflag = False
    keys = {}
    @classmethod
    def update(cls):
        for event in pygame.event.get():
            if event.type == QUIT:
                cls.quitflag = True
            if event.type == KEYUP:
                cls.keys[event.key] = False
            if event.type == KEYDOWN:
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
        self.transform.rotate((0, 0.05, 0))

class ExampleMoveComponent(Component):
    def start(self):
        self.speed = 0.005
    def update(self):
        speed = self.speed
        if Input.getkey(K_z): speed *= 2
        if Input.getkey(K_UP): self.transform.move((0,0,speed))
        if Input.getkey(K_DOWN): self.transform.move((0,0,-speed))
        if Input.getkey(K_RIGHT): self.transform.move((speed,0,0))
        if Input.getkey(K_LEFT): self.transform.move((-speed,0,0))
        if Input.getkey(K_w): self.transform.move((0,speed,0))
        if Input.getkey(K_s): self.transform.move((0,-speed,0))

class ExampleGame(Game):
    def __init__(self):
        Game.__init__(self)
        
        cameraobj = GameObject()
        cameraobj.addcomponent(Camera((0,0,10)))
        cameraobj.addcomponent(ExampleMoveComponent())
        lightobj = GameObject(Transform((0,10,0)))
        lightobj.addcomponent(Light())
        cubeobj1 = GameObject(Transform((0,0,0)))
        cubeobj1.addcomponent(Cube(color=(1,0,0,1)))
        cubeobj2 = GameObject(Transform((0,2,2)))
        cubeobj2.addcomponent(Cube(color=(0,0,1,1)))
        cubeobj2.addcomponent(ExampleComponent())
        cubeobj3 = GameObject(Transform((0,-2,-5)))
        cubeobj3.addcomponent(Cube(color=(0,1,0,1)))
        
        self.addgameobject(cameraobj)
        self.addgameobject(lightobj)
        self.addgameobject(cubeobj1)
        self.addgameobject(cubeobj2)
        self.addgameobject(cubeobj3)

game = ExampleGame()
game.mainloop()
