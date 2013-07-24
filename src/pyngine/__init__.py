import random
import math
import os

# Pygame and PyOpenGL dependencies
import pygame
import OpenGL.GL as GL
import OpenGL.GLUT as GLUT

import geom
from openglrenderer import OpenGLRenderer
from physics import PhysicsEngine
from input import Input



# ==============================
# Component & Subclasses
# ==============================

class Component(object):
    """Base class for all components"""

    def __init__(self):
        self.gameobject = None

    @property
    def transform(self):
        """Reference to the attached gameobject's transform"""
        return self.gameobject.transform
    
    @property
    def rigidbody(self):
        """Reference to the attached gameobject's rigidbody"""
        return self.gameobject.rigidbody
    
    @property
    def collider(self):
        """Reference to the attached gameobject's collider"""
        return self.gameobject.collider
    
    def start(self):
        """Called when the component is added to the game object"""
        pass
    
    def update(self):
        """
        Called in each iteration of the gameloop.
        
        For example::
        
            class MyComponent(Component):
                def update(self):
                    # Move 0.1 each step in the y-axis
                    self.transform.translate((0, .1, 0))
        """
        pass
    
    def lateupdate(self):
        """Called after all the updates of the attached gameobject's components"""
        pass
    
    def oncollision(self, other):
        """
        Called in each iteration of the gameloop when the attached gameobject has 
        collided with another gameobject. *other* is the gameobject which has collided 
        with the component's gameobject 
        """
        pass
    
    def handlemessage(self, string, data):
        """
        Calls dynamically a method of the component. *string* is the name of the method
        and *data* is the argument list for that method. It raises a ``TypeError`` if
        the component does not have the specified attribute
        """
        if string in dir(Component):
            raise TypeError, "Cannot call Component class methods"
        if hasattr(self, string):
            return self.__getattribute__(string)(*data)


class Renderable(Component):
    """Component used for enabling 3D rendering of a gameobject"""

    def __init__(self, color):
        Component.__init__(self)
        self.gl_list = GL.glGenLists(1)
        self.color = color
        
    def render(self):
        OpenGLRenderer.render(self)


class Cube(Renderable):
    """Renderable component for displaying a cube"""

    def __init__(self, color=(0, 0, 0, 1)):
        Renderable.__init__(self, color)
        GL.glNewList(self.gl_list, GL.GL_COMPILE)
        GLUT.glutSolidCube(1)
        GL.glEndList()


class Sphere(Renderable):
    """Renderable component for displaying a sphere"""

    slices = 18
    stacks = 18
    
    def __init__(self, color=(0, 0, 0, 1)):
        Renderable.__init__(self, color)
        GL.glNewList(self.gl_list, GL.GL_COMPILE)
        GLUT.glutSolidSphere(.5, Sphere.slices, Sphere.stacks)
        GL.glEndList()


class Torus(Renderable):
    """Renderable component for displaying a torus"""

    slices = 15
    rings = 15
    
    def __init__(self, inner=1, outer=1, color=(0, 0, 0, 1)):
        Renderable.__init__(self, color)
        GL.glNewList(self.gl_list, GL.GL_COMPILE)
        f = inner + outer * 2.
        GLUT.glutSolidTorus(inner/(f*2.), outer/f, Torus.slices, Torus.rings)
        GL.glEndList()


class Mesh(Renderable):
    """Renderable component for imported meshes"""

    def __init__(self, filename):
        """
        Loads a mesh from an OBJ file. *filename* is the string that indicates the
        path to the OBJ file
        """
        Renderable.__init__(self, (0,0,0,1))
        filename = os.path.join(Mesh.mesh_folder, filename)
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []
        self.material = None
        for line in open(filename, 'r'):
            values = self._process_line(line)
            if not values:
                continue
            elif values[0] == 'v':
                v = map(float, values[1:4])
                self.vertices.append(v)
            elif values[0] == 'vn':
                v = map(float, values[1:4])
                self.normals.append(v)
            elif values[0] == 'vt':
                self.texcoords.append(map(float, values[1:3]))
            elif values[0] in ('usemtl', 'usemat'):
                self.material = values[1]
            elif values[0] == 'mtllib':
                self.mtl = self._mtl(values[1])
            elif values[0] == 'f':
                self._process_face(values[1:])
        GL.glNewList(self.gl_list, GL.GL_COMPILE)
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glFrontFace(GL.GL_CCW)
        self._process_faces()
        GL.glDisable(GL.GL_TEXTURE_2D)
        GL.glEndList()

    def _process_line(self, line):
        if not line.startswith('#'):
            return line.split()

    def _mtl(self, filename):
        contents = {}
        mtl = None
        for line in open(filename, 'r'):
            values = self._process_line(line)
            if not values:
                continue
            elif values[0] == 'newmtl':
                mtl = contents[values[1]] = {}
            elif mtl is None:
                raise ValueError, "MTL file does not start with newmtl stmt"
            elif values[0] == 'map_Kd':
                self._load_texture_referred(mtl, values)
            else:
                mtl[values[0]] = map(float, values[1:])
        return contents
    
    def _load_texture_referred(self, mtl, values):
        mtl[values[0]] = values[1]
        surf = pygame.image.load(mtl['map_Kd'])
        image = pygame.image.tostring(surf, 'RGBA', 1)
        ix, iy = surf.get_rect().size
        texid = mtl['texture_Kd'] = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texid)
        GL.glTexParameteri(GL.GL_TEXTURE_2D,
                        GL.GL_TEXTURE_MIN_FILTER,
                        GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D,
                        GL.GL_TEXTURE_MAG_FILTER,
                        GL.GL_LINEAR)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA,
                     ix, iy, 0, GL.GL_RGBA,
                     GL.GL_UNSIGNED_BYTE, image)
    
    def _load_face(self, values):
        face = []
        texcoords = []
        norms = []
        for v in values:
            w = v.split('/')
            face.append(int(w[0]))
            if len(w) >= 2 and len(w[1]) > 0:
                texcoords.append(int(w[1]))
            else:
                texcoords.append(0)
            if len(w) >= 3 and len(w[2]) > 0:
                norms.append(int(w[2]))
            else:
                norms.append(0)
        self.faces.append((face, norms, texcoords, self.material))
    
    def _process_faces(self):
        for face in self.faces:
            vertices, normals, texture_coords, material = face
            mtl = self.mtl[material]
            if 'texture_Kd' in mtl:
                GL.glBindTexture(GL.GL_TEXTURE_2D, mtl['texture_Kd'])
            else:
                GL.glColor(*mtl['Kd'])
            GL.glBegin(GL.GL_POLYGON)
            for i, (vertex, normal) in enumerate(zip(vertices, normals)):
                if normal > 0:
                    GL.glNormal3fv(self.normals[normal - 1])
                if texture_coords[i] > 0:
                    GL.glTexCoord2fv(self.texcoords[texture_coords[i] - 1])
                GL.glVertex3fv(self.vertices[vertex - 1])
            GL.glEnd()            


class Audio(Component):
    """Component used to play an audio file"""
    
    def __init__(self, filename):
        """
        Creates an audio component from an audio file. *filename* is the string that
        indicates the path to the audio file
        """
        Component.__init__(self)
        self.sound = pygame.mixer.Sound(filename)
    
    @property
    def volume(self):
        """The volume of the audio file"""
        self.sound.get_volume()
    
    @volume.setter
    def volume(self, value):
        self.sound.set_volume(value)
    
    def play(self, loops=0, maxtime=0, fade_ms=0):
        """
        Plays the audio sound. *loops* indicates the number of times that the 
        """
        self.sound.play(loops, maxtime, fade_ms)
    
    def stop(self):
        """Stops the audio sound"""
        self.sound.stop()


class Particle(object):
    def __init__(self, position, direction,
                 size=.5, color=(0,0,0), life=1):
        self.position = position
        self.direction = direction
        self.size = size
        self.color = color
        self.life = life
    
    def update(self):
        if self.life > 0:
            x, y ,z = self.position
            xi, yi, zi = self.direction
            self.position = x+xi, y+yi, z+zi
        self.life -= 0.01
    
    def render(self):
        x, y, z = self.position
        color = self.color[:3] + (self.life,)
        GL.glPushMatrix()
        GL.glColor(*color)
        GL.glTranslate(x, y, -z)
        GLUT.glutSolidSphere(self.size * self.life, 5, 5)
        GL.glPopMatrix()


class ParticleEmitter(Renderable):
    def __init__(self, num_particles=15):
        Component.__init__(self)
        self.num_particles = num_particles
        self.particles = []
    
    def oncollision(self, other):
        step = int(360 / self.num_particles)
        for x in xrange(0, 360, step):
            a = x * math.pi / 180
            position = self.transform.position
            direction = math.sin(a)*0.1, 0, math.cos(a)*0.1
            color = random.random(), random.random(), 1
            particle = Particle(position, direction,
                                color=color, size=.25)
            self.particles.append(particle)
    
    def update(self):
        for particle in self.particles:
            if particle.life > 0:
                particle.update()
            else:
                self.particles.remove(particle)
    
    def render(self):
        for particle in self.particles:
            particle.render()


class Rigidbody(Component):
    """Component that simulates the mechanics of a rigid body"""
    
    def __init__(self, density):
        """
        Initializes the rigidbody representation. *density* is the integer that indicates
        the density of the body
        """
        Component.__init__(self)
        self.density = density
        self._body = PhysicsEngine.createbody()
        
    def start(self):
        mass = PhysicsEngine.createmass()
        mass.setBox(self.density, *self.transform.scale)
        self._body.setMass(mass)
        self._body.setPosition(self.transform.position)
        self._body.setQuaternion(self.transform.rotation)
        self.transform._setbody(self._body)
        if self.collider is not None:
            self._setcollider()
    
    def _setcollider(self):
        self.collider._setbody(self._body)
        
    def addforce(self, force):
        """Adds a force to the rigidbody"""
        self._body.addForce(force)
        
    def isenabled(self):
        """Returns whether the rigidbody is enabled or not"""
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
    
    def enable(self):
        self._body.enable()
    
    def disable(self):
        self._body.disable()


class Collider(Component):
    """Component used for collision detection"""

    def __init__(self):
        Component.__init__(self)
        self._geom = None
        
    def _fixedstart(self):
        self._geom.gameobject = self.gameobject
        self._geom.setPosition(self.transform.position)
        self._geom.setQuaternion(self.transform.rotation)
        self.transform._setgeom(self._geom)
        if self.rigidbody:
            self.rigidbody._setcollider()
        
    def _setbody(self, body):
        self._geom.setBody(body)
        
    def _clearbody(self):
        self._geom.setBody(None)
    
    def disable(self):
        self._geom.disable()
    
    def enable(self):
        self._geom.enable()


class BoxCollider(Collider):
    """Collider with a box shape"""
    
    def __init__(self):
        Collider.__init__(self)
        
    def start(self):
        scale = self.transform.scale
        self._geom = PhysicsEngine.creategeom("Box", (scale,))
        self._fixedstart()


class SphereCollider(Collider):
    """Collider with a sphere shape"""
    
    def __init__(self):
        Collider.__init__(self)
        
    def start(self):
        radius = self.transform.scale[0]/2.
        self._geom = PhysicsEngine.creategeom("Sphere", (radius,))
        self._fixedstart()


class Transform(Component):
    """
    Component that stores the gameobject transform properties:
    
    * Position
    * Rotation
    * Scale
    """

    def __init__(self, position=(0, 0, 0), rotation=(1,0,0,0),
                 scale=(1, 1, 1)):
        Component.__init__(self)
        self._position = position
        self._rotation = rotation
        self._scale = scale
        self._children = []
        self._geom = None
        self._body = None
    
    def _setgeom(self, geom):
        """
        Adds a reference to the geom of the gameobject's collider
        """
        self._geom = geom
        
    def _cleargeom(self):
        """
        Set the reference to the geom of the gameobject's collider to None
        """
        self._geom = None
    
    def _setbody(self, body):
        """
        Adds a reference to the body of the gameobject's rigidbody
        """
        self._body = body
        
    def _clearbody(self):
        """Set the reference to the body of the gameobject's rigidbody to None
        """
        self._body = None
        
    @property
    def position(self):
        result = self._position
        if self._body is not None:
            result = self._body.getPosition()
        elif self._geom is not None:
            result = self._geom.getPosition()
        return geom.Vector3D(*result)
    
    @position.setter
    def position(self, value):
        startposition = self.position
        if self._body is not None:
            self._body.setPosition(value)
        elif self._geom is not None:
            self._geom.setPosition(value)
        self._position = value
        offset = self.position - startposition
        for child in self._children:
            child.translate(offset)
    
    @property
    def rotation(self):
        result = self._rotation
        if self._body is not None:
            result = self._body.getQuaternion()
        elif self._geom is not None:
            result = self._geom.getQuaternion()
        return geom.Quaternion(*result)
    
    @rotation.setter
    def rotation(self, value):
        if self._body is not None:
            self._body.setQuaternion(value)
        if self._geom is not None:
            self._geom.setQuaternion(value)
        self._rotation = value

    @property
    def scale(self):
        return self._scale
    
    @scale.setter
    def scale(self, value):
        self._scale = value

    @property
    def right(self):
        q = geom.Quaternion(*self.rotation)
        return q.rotate_vector([1, 0, 0])

    @property
    def up(self):
        q = geom.Quaternion(*self.rotation)
        return q.rotate_vector([0, 1, 0])

    @property
    def forward(self):
        q = geom.Quaternion(*self.rotation)
        return q.rotate_vector([0, 0, 1])

    def translate(self, movement):
        """
        Moves the transform a certain offset
        """
        self.position = self.position + movement

    def rotate(self, axis, angle):
        """
        Rotates the transform a certain offset
        """
        q1 = self.rotation
        q2 = geom.Quaternion.from_axis(axis, angle)
        self.rotation = q1 * q2
        for child in self._children:
            child.rotate(axis, angle)
    
    def addchild(self, child):
        """
        Adds a Transform to its children
        """
        self._children.append(child)
    
    def __iter__(self):
        return self._children.__iter__()


class Camera(Component):    
    def __init__(self, distance=(0, 0, 0), orientation=(0, 0, 0)):
        Component.__init__(self)
        self.distance = distance
        self.orientation = orientation
        
    def push(self):
        dx, dy, dz = self.distance
        x, y, z = self.transform.position
        a, b, c = self.orientation
        GL.glPushMatrix()
        GL.glTranslatef(-dx, -dy, -dz)
        GL.glRotatef(-a, 1, 0, 0)
        GL.glRotatef(-b, 0, 1, 0)
        GL.glRotatef(c, 0, 0, 1)
        GL.glTranslatef(-x, -y, z)

    def pop(self):
        GL.glPopMatrix()


class Light(Component):
    def __init__(self, ambient=(0, 0, 0, 1), diffuse=(1, 1, 1, 1),
                 specular=(1, 1, 1, 1), spot_direction=(0, 0, 1)):
        Component.__init__(self)
        self.gl_light = OpenGLRenderer.getnextlight()
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.spot_direction = spot_direction + (0,)
        self.directional = False
        
    def enable(self):
        if self.gl_light is not None:
            x, y, z = self.transform.position
            gl_position = (x, y, -z, int(not self.directional))
            OpenGLRenderer.enablelight(self.gl_light, self.ambient,
                                       self.diffuse, self.specular,
                                       self.spot_direction, gl_position)
            
    def disable(self):
        if self.gl_light is not None:
            OpenGLRenderer.disable(self.gl_light)
            


# ==============================
# GameObject & Primitives
# ==============================

class GameObject(object):
    
    _gameobjects = []
    _camera = None
    _lights = []
    
    def __init__(self, transform=Transform(), *components):
        self.name = ''
        self.tag = ''
        self.transform = None
        self.rigidbody = None
        self.collider = None
        self.renderables = []
        self.components = []
        self.addcomponent(transform)
        for c in components: self.addcomponent(c)
        GameObject._gameobjects.append(self)
        
    def getcomponentbyclass(self, cls):
        """
        Returns an attached component of a specific class
        
        Parameters
        ----------
        cls : classobj
            Class of the component
        """
        for c in self.components:
            if isinstance(c, cls):
                return c
    
    def addcomponents(self, *components):
        for component in components:
            self.addcomponent(component)

    def addcomponent(self, component):
        """
        Adds a component to the gameobject
        """
        if isinstance(component, Camera):
            GameObject._camera = component
        self._updatecomponents('append', component)
        self._checkfield('transform', component)
        self._checkfield('rigidbody', component)
        self._checkfield('collider', component)
        component.gameobject = self
        component.start()
        
    def removecomponent(self, component):
        """
        Removes a component from the gameobject
        """
        if component is None: return
        if isinstance(component, Camera):
            GameObject._camera = None
        self._updatecomponents('remove', component)
        Component.__init__(component)

    def _checkfield(self, cls_string, component):
        cls = eval(cls_string.capitalize())
        if isinstance(component, cls):
            oldcomponent = self.__dict__[cls_string]
            self.__dict__[cls_string] = component
            self.removecomponent(oldcomponent)
            
    def _updatecomponents(self, action, component):
        if isinstance(component, Light):
            getattr(GameObject._lights, action)(component)
        if isinstance(component, Component):
            getattr(self.components, action)(component)
        if isinstance(component, Renderable):
            getattr(self.renderables, action)(component)
            
    def handle_message(self, string, data=None):
        for component in self.components:
            result = component.handle_message(string, data)
            if result is not None:
                return result

    def update(self):
        """
        Updates the gameobject and its children
        """
        for component in self.components:
            component.update()
    
    def lateupdate(self):
        """
        Called after all updates
        """
        for component in self.components:
            component.lateupdate()

    def render(self):
        """
        Renders the gameobject and its children
        """
        for component in self.renderables:
            component.render()

    def oncollision(self, other):
        for component in self.components:
            component.oncollision(other)

    def destroy(self):
        """
        Removes a the gameobject from the scene
        """
        try:
            GameObject._gameobjects.remove(self)
            if self.rigidbody is not None:
                self.rigidbody.disable()
                self.rigidbody = None
            if self.collider is not None:
                self.collider.disable()
                self.collider = None
        except:
            print("WARNING: This object is already removed")


class CubePrimitive(GameObject):
    """
    Primitive for a basic solid cube
    """
    def __init__(self, transform, color, density=10):
        """
        Parameters
        ----------
        transform : Transform
        color : Color
        density : int
        """
        GameObject.__init__(self, transform, Rigidbody(density),
                            Cube(color), BoxCollider())


class SpherePrimitive(GameObject):
    """
    Primitive for a basic solid sphere
    """
    def __init__(self, transform, color, density=10):
        """
        Parameters
        ----------
        transform : Transform
        color : Color
        density : int
        """
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
    def __init__(self, r, g, b, a):
        self.__color = (r, g, b, a)
    def __getitem__(self, index):
        return self.__color[index]
    def __repr__(self):
        return self.__color



# ==============================
# Game
# ==============================

class Scene(object):
    """
    Root gameobject of a game
    """
    def __init__(self, gravity=(0, -9.8, 0), erp=.8, cfm=1e-5):
        """
        Initializes the physics for the current scene
        """
        PhysicsEngine.start(gravity, erp, cfm)


class Game(object):
    
    delta = 0.
    scale = 1.
    
    def __init__(self, screen_size=(800, 600), fullscreen=False):
        """
        Initializes the game
        """
        self.screen_size = screen_size
        self.fullscreen = fullscreen
        self.title = "Pyngine game"
        self.icon = None
        self.camera = None
        self.lights = []
        self.scene = Scene()
        
    def mainloop(self, fps=60):
        """
        Starts the mainloop of the game
        """
        OpenGLRenderer.init(self.screen_size, self.fullscreen)
        OpenGLRenderer.set_window_title(self.title)        
        OpenGLRenderer.set_window_icon(self.icon)
        try: self._mainloop(fps)
        finally: OpenGLRenderer.quit()
            
    def _mainloop(self, fps):
        step = 1. / fps
        clock = pygame.time.Clock()
        while not Input.quitflag:
            Input.update()
            map(GameObject.update, GameObject._gameobjects)
            #self.scene.lateupdate()
            self._renderloop()
            PhysicsEngine.step(step * Game.scale)
            delta = clock.tick(fps)
            Game.delta = delta / 1000.
            
    def _renderloop(self):
        OpenGLRenderer.clearscreen()
        if GameObject._camera: GameObject._camera.push()
        for light in GameObject._lights: light.enable()
        map(GameObject.render, GameObject._gameobjects)
        if GameObject._camera: GameObject._camera.pop()
        OpenGLRenderer.flip()

