import math


class MetaVector3D(type):
    @property
    def right(cls): return cls(1, 0, 0)  # @NoSelf
    @property
    def up(cls): return cls(0, 1, 0)  # @NoSelf
    @property
    def forward(cls): return cls(0, 0, 1)  # @NoSelf


class Vector3D(tuple):
    
    __metaclass__ = MetaVector3D

    def __new__(cls, x, y, z):
        return tuple.__new__(cls, (x,y,z))

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    @property
    def z(self):
        return self[2]
    
    def __add__(self, other):
        return Vector3D(*[a+b for a,b in zip(self, other)])
    
    
    def __sub__(self, other):
        return Vector3D(*[a-b for a,b in zip(self, other)])
    
    def __mul__(self, factor):
        return Vector3D(*[n * factor for n in self])


class Quaternion(tuple):
    
    def __new__(cls, w, x, y, z):
        return tuple.__new__(cls, (w,x,y,z))
    
    @property
    def conjugate(self):
        return Quaternion(self.w, -self.x, -self.y, -self.z)
    
    @property
    def round(self):
        return Quaternion(*map(round, self))
    
    @property
    def w(self):
        return self[0]    
    
    @property
    def x(self):
        return self[1]
    
    @property
    def y(self):
        return self[2]
    
    @property
    def z(self):
        return self[3]

    def __repr__(self):
        return "Quaternion(%s, %s, %s, %s)" % (self.w, self.x, self.y, self.z)

    def __mul__(self, rq):
        w, x, y, z = self
        rw, rx, ry, rz = rq
        return Quaternion(w*rw - x*rx - y*ry - z*rz,
                          w*rx + x*rw + y*rz - z*ry,
                          w*ry + y*rw + z*rx - x*rz,
                          w*rz + z*rw + x*ry - y*rx)

    def rotate_vector(self, v):
        s = sum(v, 0.0)
        vn = [i/s for i in v]
        vquat = Quaternion(0.0, vn[0], vn[1], vn[2])
        resquat = vquat * self.conjugate
        resquat = self * resquat
        return Vector3D(resquat.x, resquat.y, resquat.z)

    @staticmethod
    def from_axis(axis, angle):
        s = sum(axis, 0.0)
        axis = [n/s for n in axis]
        angle *= 0.5
        sin = math.sin(angle)
        cos = math.cos(angle)
        return Quaternion(cos, axis[0] * sin, axis[1] * sin, axis[2] * sin)

