from OpenGL.GL import * # @UnusedWildImport


class Particle(object):
    def __init__(self, position, rotation, direction,
                 size=.5, color=(0,0,0), life=1):
        self.position = position
        self.rotation = rotation
        self.direction = direction
        self.size = size
        self.color = color
        self.life = life
    
    def update(self):
        if self.life > 0:
            self.position[0] += self.direction[0]
            self.position[1] += self.direction[1]
            self.position[2] += self.direction[2]
        self.life -= 0.0001
    
    def render(self):
        glPushMatrix()
        glColor(*(self.color[:3]+self.life))
        glTranslate(self.position)
        glBegin()
        glTexCoord(0,0);glVertex(-self.size, self.size, 0)
        glTexCoord(0,1);glVertex(-self.size, -self.size, 0)
        glTexCoord(1,1);glVertex(self.size, -self.size, 0)
        glTexCoord(1,0);glVertex(self.size, self.size, 0)
        glEnd()
        glPopMatrix()


class ParticleEmitter(object):
    pass
