from pyngine import * # @UnusedWildImport


class Jump(Component):
    def start(self):
        self.speed = .2
        self.jumpforce = 200
        self.canjump = False
    def update(self):
        body = self.gameobject.rigidbody
        x, y, z = body.velocity
        if Input.getkey(pygame.K_a):
            if x > 0: x/10.
            body.velocity = (x-self.speed,y,z)
        if Input.getkey(pygame.K_d):
            if x < 0: x/10.
            body.velocity = (x+self.speed,y,z)
        if Input.getkey(pygame.K_w) and self.canjump:
            self.canjump = False
            body.addforce((0,self.jumpforce,0))
    def oncollision(self, other):
        self.canjump = True


class Platform(GameObject):
    def __init__(self, pos, size):
        GameObject.__init__(self, Transform(position=pos, scale=size))
        self.addcomponents(Cube(color=Color.white), BoxCollider(), Rigidbody(10000))
        self.rigidbody.usegravity = False
        

class Platformer(Game):
    def __init__(self):
        Game.__init__(self)
        light = GameObject(Transform((0,5,-5)))
        light.addcomponent(Light())
        
        platform1 = Platform(pos=(0, 1 ,0), size=(10, 1, 2))
        platform2 = Platform(pos=(11.5, 2, 0), size=(10, 1, 2))
        platform3 = Platform(pos=(-12, 4, 0), size=(10, 1, 2))

        woman = GameObject(Transform((8, 3, 0), scale=(.5,.5,.5)), Mesh('woman.obj'))

        sphere = GameObject(Transform((0, 7, 0)), Sphere(color=Color.green), SphereCollider(), Rigidbody(1))
        sphere.addcomponents(Camera((0, 0, 20)), Jump())
        self.scene.addgameobjects(light, platform1, platform2, platform3, sphere, woman)

if __name__ == "__main__":
    p = Platformer()
    p.mainloop()
