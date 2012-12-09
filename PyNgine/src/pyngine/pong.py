from pyngine import * #@UnusedWildImport
from pygame import K_UP, K_DOWN, K_w, K_s


class KeyboardMovement(Component):
    def __init__(self, up, dowm):
        Component.__init__(self)
        self.speed = 0.2
        self.up = up
        self.down = dowm
    def update(self):
        z = self.transform.position[2]
        if Input.getkey(self.up) and z < 7:
            self.transform.move((0, 0, self.speed))
        if Input.getkey(self.down) and z > -7:
            self.transform.move((0, 0, -self.speed))

class ArrowMovement(KeyboardMovement):
    def __init__(self):
        KeyboardMovement.__init__(self, K_UP, K_DOWN)

class WSMovement(KeyboardMovement):
    def __init__(self):
        KeyboardMovement.__init__(self, K_w, K_s)

class BallMovement(Component):
    def start(self):
        self.movement = (.1, 0, .1)
    def update(self):
        self.transform.move(self.movement)
    def oncollision(self, other):
        x, _, z = self.movement
        if other.tag == 'Player': x *= -1.025
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
                            Sphere(color=Color.white), BallMovement())

class Pong(Game):
    def __init__(self):
        Game.__init__(self)
        cameraobj = GameObject(Transform(), Camera((0, 0, 40), (-45, 0, 0)))
        lightobj = GameObject(Transform((0, 7, 0)), Light())
        paddle1 = Paddle(pos=(-8, 0, 0), movement=WSMovement())
        paddle2 = Paddle(pos=(8, 0, 0), movement=ArrowMovement())
        limit1 = Limit(pos=(0, 0, 10))
        limit2 = Limit(pos=(0, 0, -10))
        ball = Ball(pos=(0, 0, -5))
        self.scene.addgameobjects(cameraobj, lightobj, paddle1, paddle2, ball, limit1, limit2)


if __name__ == "__main__":
    game = Pong()
    game.mainloop()
