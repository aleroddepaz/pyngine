import math

class Quaternion(object):
    def __init__(self, w=1, x=0, y=0, z=0):
        self.w = w
        self.x = x
        self.y = y
        self.z = z
    
    @property
    def conjugate(self):
        return Quaternion(self.w, -self.x, -self.y, -self.z)
    
    def __iter__(self):
        yield self.w
        yield self.x
        yield self.y
        yield self.z
    
    def __getitem__(self, key):
        if key == 0: return self.w
        elif key == 1: return self.x
        elif key == 2: return self.y
        elif key == 3: return self.z
    
    def __setitem__(self, key, value):
        if key == 0: self.w = value
        elif key == 1: self.x = value
        elif key == 2: self.y = value
        elif key == 3: self.z = value

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
        return [resquat.x, resquat.y, resquat.z]

    @staticmethod
    def from_axis(axis, angle):
        angle *= 0.5
        s = sum(axis, 0.0)
        axis = [n/s for n in axis]
        sin = math.sin(angle)
        cos = math.cos(angle)
        return Quaternion(cos, axis[0] * sin, axis[1] * sin, axis[2] * sin)

