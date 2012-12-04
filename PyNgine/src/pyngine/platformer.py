from pyngine import * # @UnusedWildImport


class Jump(Component):
    def __init__(self):
        self.speed = .2
        self.jumpforce = 200
        self.canjump = False
    def update(self):
        body = self.gameobject.rigidbody
        x, y, z = body.velocity
        if Input.getkey(pygame.K_a): body.velocity = (x-self.speed,y,z)
        if Input.getkey(pygame.K_d): body.velocity = (x+self.speed,y,z)
        if Input.getkey(pygame.K_w) and self.canjump:
            self.canjump = False
            body.addforce((0,self.jumpforce,0))
    def oncollision(self, other):
        self.canjump = True


class Platform(GameObject):
    def __init__(self, pos, size):
        GameObject.__init__(self, Transform(position=pos, size=size))
        self.addcomponents(Cube(color=Color.white), BoxCollider(), Rigidbody(10000))
        self.rigidbody.usegravity = False
        

class Platformer(Game):
    def __init__(self):
        Game.__init__(self)
        light = GameObject(Transform((0,10,-5)))
        light.addcomponent(Light())
        
        platform1 = Platform(pos=(0,1,0), size=(10,1,2))
        platform2 = Platform(pos=(12,3,0), size=(10,1,2))

        sphere = GameObject(Transform((0,10,0)), Sphere(color=Color.green), SphereCollider(), Rigidbody(1))
        sphere.addcomponent(Camera((0, 0, 20)), Jump())
        self.scene.addgameobjects(platform1, platform2, sphere)

if __name__ == "__main__":
    p = Platformer()
    p.mainloop()
