from pyngine import * #@UnusedWildImport


class KeyboardMovement(Component):
    def __init__(self, up, dowm):
        Component.__init__(self)
        self.speed = 0.2
        self.up = up
        self.down = dowm
    def update(self):
        z = self.transform.position[2]
        if Input.getkey(self.up) and z < 7:
            self.transform.translate((0, 0, self.speed))
        if Input.getkey(self.down) and z > -7:
            self.transform.translate((0, 0, -self.speed))

class ArrowMovement(KeyboardMovement):
    def __init__(self):
        KeyboardMovement.__init__(self, pygame.K_UP, pygame.K_DOWN)

class WSMovement(KeyboardMovement):
    def __init__(self):
        KeyboardMovement.__init__(self, pygame.K_w, pygame.K_s)

class BallMovement(Component):
    def start(self):
        self.start_position = self.transform.position
        self.movement = (.1, 0, .1)
        self.last_collision = None
    def update(self):
        self.transform.translate(self.movement)
        x = self.transform.position[0]
        if x > 30 or x < -30:
            self.transform.position = self.start_position
            self.movement = (.1, 0, .1)
    def oncollision(self, other):
        x, _, z = self.movement
        if other.tag == 'Player' and self.last_collision is not other:
            self.last_collision = other
            x *= -1.025
        elif other.tag == 'Limit': z *= -1.01
        self.movement = (x, 0, z)

class Paddle(GameObject):
    def __init__(self, pos, movement):
        GameObject.__init__(self, Transform(position=pos, scale=(1, 1, 5)),
                            BoxCollider(), Cube(Color.blue), movement)
        self.tag = 'Player'

class Limit(GameObject):
    def __init__(self, pos):
        GameObject.__init__(self, Transform(position=pos, scale=(30, 1, 1)),
                            BoxCollider(), Cube(Color.green))
        self.tag = 'Limit'

class Ball(GameObject):
    def __init__(self, pos):
        GameObject.__init__(self, Transform(position=pos), SphereCollider(),
                            Sphere(color=Color.white), BallMovement(), ParticleEmitter())

class Pong(Game):
    def __init__(self):
        Game.__init__(self)
        GameObject(Transform(), Camera((0, 0, 40), (-45, 0, 0)))
        GameObject(Transform((0, 7, 0)), Light())
        Paddle(pos=(-8, 0, 0), movement=WSMovement())
        Paddle(pos=(8, 0, 0), movement=ArrowMovement())
        Limit(pos=(0, 0, 10))
        Limit(pos=(0, 0, -10))
        Ball(pos=(0, 0, -5))


if __name__ == "__main__":
    game = Pong()
    game.mainloop()
