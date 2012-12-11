import pygame
from OpenGL.GL import * # @UnusedWildImport
from OpenGL.GLU import * # @UnusedWildImport
from OpenGL.raw.GLUT import * # @UnusedWildImport
from openglrenderer import *
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
        if self.color is not None:
            glColor(*self.color)
        glCallList(self.gl_list)
        glPopMatrix()


class Cube(Renderer):
    
    def __init__(self, color=(0, 0, 0, 1)):
        Renderer.__init__(self, color)
        glNewList(self.gl_list, GL_COMPILE)
        glutSolidCube(1)
        glEndList()


class Sphere(Renderer):
    
    slices = 18
    stacks = 18
    
    def __init__(self, color=(0, 0, 0, 1)):
        Renderer.__init__(self, color)
        glNewList(self.gl_list, GL_COMPILE)
        glutSolidSphere(.5, Sphere.slices, Sphere.stacks)
        glEndList()


class Torus(Renderer):
    
    slices = 15
    rings = 15
    
    def __init__(self, inner=1, outer=1, color=(0, 0, 0, 1)):
        Renderer.__init__(self, color)
        glNewList(self.gl_list, GL_COMPILE)
        f = inner+outer*2.
        glutSolidTorus(inner/(f*2.), outer/f, Torus.slices, Torus.rings)
        glEndList()


class Mesh(Renderer):
    
    mesh_folder = os.sep.join(['..','data','obj'])
    
    def _load_texture_referred(self, mtl, values):
        mtl[values[0]] = values[1]
        surf = pygame.image.load(mtl['map_Kd'])
        image = pygame.image.tostring(surf, 'RGBA', 1)
        ix, iy = surf.get_rect().size
        texid = mtl['texture_Kd'] = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texid)
        glTexParameteri(GL_TEXTURE_2D,
                        GL_TEXTURE_MIN_FILTER,
                        GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D,
                        GL_TEXTURE_MAG_FILTER,
                        GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                     ix, iy, 0, GL_RGBA,
                     GL_UNSIGNED_BYTE, image)

    def _mtl(self, filename):
        filename = os.sep.join([Mesh.mesh_folder, filename])
        contents = {}
        mtl = None
        for line in open(filename, 'r'):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'newmtl':
                mtl = contents[values[1]] = {}
            elif mtl is None:
                raise ValueError, "mtl file doesn't start with newmtl stmt"
            elif values[0] == 'map_Kd':
                self._load_texture_referred(mtl, values)
            else:
                mtl[values[0]] = map(float, values[1:])
        return contents

    def __init__(self, filename):
        Renderer.__init__(self, (0,0,0,1))
        filename = os.sep.join([Mesh.mesh_folder, filename])
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []
        material = None
        for line in open(filename, 'r'):
            if line.startswith('#'): continue
            values = line.split()
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
                material = values[1]
            elif values[0] == 'mtllib':
                self.mtl = self._mtl(values[1])
            elif values[0] == 'f':
                face = []
                texcoords = []
                norms = []
                for v in values[1:]:
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
                self.faces.append((face, norms, texcoords, material))
        glNewList(self.gl_list, GL_COMPILE)
        glEnable(GL_TEXTURE_2D)
        glFrontFace(GL_CCW)
        for face in self.faces:
            vertices, normals, texture_coords, material = face
            mtl = self.mtl[material]
            if 'texture_Kd' in mtl:
                glBindTexture(GL_TEXTURE_2D, mtl['texture_Kd']) # use diffuse texmap
            else:
                glColor(*mtl['Kd']) # just use diffuse colour
            glBegin(GL_POLYGON)
            for i, (vertex, normal) in enumerate(zip(vertices, normals)):
                if normal > 0:
                    glNormal3fv(self.normals[normal - 1])
                if texture_coords[i] > 0:
                    glTexCoord2fv(self.texcoords[texture_coords[i] - 1])
                glVertex3fv(self.vertices[vertex - 1])
            glEnd()
        glDisable(GL_TEXTURE_2D)
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
        
    def _fixedstart(self):
        self._geom.gameobject = self.gameobject
        self._geom.setPosition(self.transform.position)
        self._geom.setRotation(self.transform.rotation)
        self.transform._setgeom(self._geom)
        
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
        self._fixedstart()


class SphereCollider(Collider):
    
    def __init__(self):
        Collider.__init__(self)
        
    def start(self):
        radius = self.transform.scale[0]/2.
        self._geom = PhysicsEngine.creategeom("Sphere", (radius,))
        self._fixedstart()


class Transform(Component):
    
    def __init__(self, position=(0, 0, 0),
                 rotation=(1, 0, 0, 0, 1, 0, 0, 0, 1), scale=(1, 1, 1)):
        Component.__init__(self)
        self._position = position
        self._rotation = rotation
        self._scale = scale
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
        """
        Set the reference to the body of the gameobject's rigidbody to None
        """
        self._body = None
        
    @property
    def position(self):
        if self._body is not None:
            return self._body.getPosition()
        return self._position
    
    @position.setter
    def position(self, value):
        if self._body is not None:
            self._body.setPosition(value)
        if self._geom is not None:
            self._geom.setPosition(value)
        self._position = value
    
    @property
    def rotation(self):
        if self._body is not None:
            return self._body.getRotation()
        return self._rotation
    
    @rotation.setter
    def rotation(self, value):
        if self._body is not None:
            self._body.setRotation(value)
        self._rotation = value

    @property
    def scale(self):
        return self._scale
    
    @scale.setter
    def scale(self, value):
        self._scale = value

    def move(self, movement):
        """
        Moves the transform a certain offset
        """
        self.position = tuple(map(sum, zip(self.position, movement)))

    def rotate(self, rotation):
        """
        Rotates the transform a certain offset
        """
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



class Scene(GameObject):
    def __init__(self, gravity=(0, -9.8, 0), erp=.8, cfm=1e-5):
        GameObject.__init__(self, Transform())
        PhysicsEngine.start(gravity, erp, cfm)


class Game(object):
    
    def __init__(self, screensize=(800, 600), title="Pyngine game",
                 hwsurface=False, path_to_icon=None):
        self.screensize = screensize
        self.title = title
        self.camera = None
        self.lights = []
        self.scene = Scene()
        OpenGLRenderer.init(screensize, hwsurface)
        OpenGLRenderer.setwindowtitle(title)        
        OpenGLRenderer.setwindowicon(path_to_icon)
        OpenGLRenderer.dostuff()
        OpenGLRenderer.enable()
        
    def mainloop(self, fps=60):
        try:
            self._mainloop(fps)
        except Error as e:
            print "Oops! %s: %s" % (e.errno, e.strerror)
        finally:
            OpenGLRenderer.quit()
            
    def _mainloop(self, fps):
        step = 1. / fps
        clock = pygame.time.Clock()
        while not Input.quitflag:
            Input.update()
            self.scene.update()
            self._renderloop()
            PhysicsEngine.step(step)
            clock.tick(fps)
            
    def _renderloop(self):
        OpenGLRenderer.setviewport()
        OpenGLRenderer.setperspective()
        OpenGLRenderer.initmodelviewmatrix()
        OpenGLRenderer.clearscreen()
        if GameObject._camera: GameObject._camera.push()
        for light in GameObject._lights: light.enable()
        self.scene.render()
        if GameObject._camera: GameObject._camera.pop()
        OpenGLRenderer.flip()
