from pyngine import * #@UnusedWildImport


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
        KeyBoardMovement.__init__(self, pygame.K_UP, pygame.K_DOWN)

class WSMovement(KeyBoardMovement):
    def __init__(self):
        KeyBoardMovement.__init__(self, pygame.K_w, pygame.K_s)

class BallMovement(Component):
    def start(self):
        self.rigidbody.velocity = (10, 0, 5)
    def oncollision(self, other):
        x, _, z = self.rigidbody.velocity
        if other.tag == 'Player': x *= -1
        else: z *= -1
        self.rigidbody.velocity = (x, 0, z)


class Paddle(GameObject):
    def __init__(self, pos):
        GameObject.__init__(self, Transform(position=pos,
                                            scale=(1, 1, 5)))
        self.addcomponents(BoxCollider(), Cube(Color.red))
        self.tag = 'Player'


class Limit(GameObject):
    def __init__(self, pos):
        GameObject.__init__(self, Transform(position=pos,
                                            scale=(30, 1, 1)))
        self.addcomponents(BoxCollider(), Cube(Color.green))
        self.tag = 'Limit'


class Pong(Game):
    def __init__(self):
        Game.__init__(self)
        lightobj = GameObject(Transform((0, 7, 0)), Light())
        
        paddle1 = Paddle(pos=(-8, 0, 0))
        paddle1.addcomponent(WSMovement())
        paddle2 = Paddle(pos=(8, 0, 0))
        paddle2.addcomponent(ArrowMovement())
        
        limit1 = Limit(pos=(0, 0, 10))
        limit2 = Limit(pos=(0, 0, -10))
        
        rigidbody = Rigidbody(1)
        rigidbody.usegravity = False
        ball = GameObject(Transform((0, 0, -5)), Sphere(), Cube(Color.white), rigidbody)
        ball.addcomponents(BallMovement(), Camera((0, 0, 30)))
        ball.tag = 'Ball'
        
        self.scene.addgameobjects(lightobj, paddle1, paddle2, ball, limit1, limit2)

        
if __name__ == "__main__":
    game = Pong()
    game.mainloop()
