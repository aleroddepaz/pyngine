from pyngine.core import * #@UnusedWildImport


class KeyBoardMovement(Component):
    def __init__(self, keyup, keydown):
        Component.__init__(self)
        self.speed = 0.2
        self.keyup = keyup
        self.keydown = keydown
    def update(self):
        speed = self.speed
        if Input.getkey(self.keyup): self.transform.move((0, 0, speed))
        if Input.getkey(self.keydown): self.transform.move((0, 0, -speed))
        
class ArrowMovement(KeyBoardMovement):
    def __init__(self):
        KeyBoardMovement.__init__(self, pgl.K_UP, pgl.K_DOWN)

class WSMovement(KeyBoardMovement):
    def __init__(self):
        KeyBoardMovement.__init__(self, pgl.K_w, pgl.K_s)

class BallMovement(Component):
    def start(self):
        self.rigidbody.velocity = (10, 0, 5)
    def oncollision(self, other):
        x, _, z = self.rigidbody.velocity
        if other.tag == 'Player': x *= -1
        else: z *= -1
        self.rigidbody.velocity = (x, 0, z)

class Pong(Game):
    def __init__(self):
        Game.__init__(self)
        cameraobj = GameObject(Transform())
        cameraobj.addcomponent(Camera(distance=(0, 0, 10), orientation=(0, 0, 0)))
        lightobj1 = GameObject(Transform((0, 7, 0)))
        lightobj1.addcomponent(Light())
        
        t1 = Transform(position=(-8, 0, 0), scale=(1, 1, 5))
        t2 = Transform(position=(8, 0, 0), scale=(1, 1, 5))
        paddle1 = CubePrimitive(transform=t1, color=Color.red)
        paddle1.addcomponent(WSMovement())
        paddle2 = CubePrimitive(transform=t2, color=Color.red)
        paddle2.addcomponent(ArrowMovement())
        
        t3 = Transform(position=(0, 0, 10), scale=(30, 1, 1))
        t4 = Transform(position=(0, 0, -10), scale=(30, 1, 1))
        limit1 = CubePrimitive(transform=t3, color=Color.black, density=10000)
        limit2 = CubePrimitive(transform=t4, color=Color.black, density=10000)
        ball = SpherePrimitive(Transform((0, 0, -5)), Color.white)
        ball.addcomponent(BallMovement())
        
        paddle1.tag = paddle2.tag = 'Player'
        limit1.tag = limit2.tag = 'Limit'
        ball.tag = 'Ball'
        
        self.scene.addgameobjects(cameraobj, lightobj1, paddle1, paddle2, ball, limit1, limit2)

        
if __name__ == "__main__":
    game = Pong()
    game.mainloop()
