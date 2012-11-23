import pygame
from pygame.locals import *
from OpenGL.GL import *


class Game(object):
    def __init__(self, screen_size, depth = 32):
        pygame.init()
        params = OPENGL | DOUBLEBUF
        # params |= FULLSCREEN
        # params |= HWSURFACE
        # params |= NOFRAME
        pygame.display.set_mode(screen_size, params, depth)
        self.isinitialized = True
    def mainloop(self):
        while self.isinitialized:
            pass #do stuff


class Component(object):
    def __init__(self):
        self.gameobject = None
    def start(self):
        pass
    def update(self):
        pass


class Transform(Component):
    def __init__(self, position=(0,0,0), rotation=(0,0,0), scale=(1,1,1)):
        self.position = position
        self.rotation = rotation
        self.scale = scale
        self.right = (1,0,0)
        self.up = (0,1,0)
        self.forward = (0,0,1)
    def rotatearound(self, other):
        pass # TO DO
    def lookat(self, other):
        pass # TO DO


class GameObject(object):
    def __init__(self, transform=Transform()):
        self.transform = transform
        self.components = []
        self.renderables = []
        self.colliders = []
    def addcomponent(self, component):
        self.__updatecomponents('append', component)
        component.gameobject = self
        component.start()
    def removecomponent(self, component):
        self.__updatecomponents('remove', component)
        component.gameobject = None
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


class ObjectLayer(pygame.Surface, GameObject):
    def __init__(self):
        self.gameobjects = []
    def addgameobject(self, go):
        self.gameobjects.append(go)
    def render(self):
        for go in self.renderables:
            go.render(0, 0, 0, 1)
            

class Renderer(Component):
    def __init__(self, fillcolor, strokecolor, strokewidth, alpha, zoom):
        self.fillcolor = fillcolor
        self.strokecolor = strokecolor
        self.strokewidth = strokewidth
        self.alpha = alpha
        self.zoom = zoom
    def render(self, x, y, angle, zoom):
        pass


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
    gl_lights = xrange(GL_LIGHT0, GL_LIGHT7+1)
    # Default values retrieved from http://www.talisman.org/opengl-1.1/Reference/glLight.html
    def __init__(self, ambient=(0,0,0,1),diffuse=(1,1,1,1),
                 specular=(1,1,1,1),spot_direction=(0,0,1)):
        Component.__init__(self)
        self.gl_light = Light.__getnextlight()
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.spot_direction = spot_direction
    def start(self):
        if self.gl_light != None:
            position = self.gameobject.transform.position
            glLightfv(self.gl_light, GL_AMBIENT, self.ambient)
            glLightfv(self.gl_light, GL_DIFFUSE, self.diffuse)
            glLightfv(self.gl_light, GL_SPECULAR, self.specular)
            glLightfv(self.gl_light, GL_SPOT_DIRECTION, self.spot_direction+(0,))
            glLightfv(self.gl_light, GL_POSITION, (position[0], position[1], -position[2], int(not self.directional)))
            glEnable(self.gl_light)
    def disable(self):
        if self.gl_light != None:
            glDisable(self.gl_light)
    @classmethod
    def __getnextlight(cls):
        try: return cls.gl_lights.pop()
        except IndexError: return None
