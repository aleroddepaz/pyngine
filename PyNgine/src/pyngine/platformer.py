from pyngine import * # @UnusedWildImport


class Qwe(Component):
    def start(self):
        Component.start(self)
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

class Platformer(Game):
    def __init__(self):
        Game.__init__(self)
        light = GameObject(Transform((0,10,-5)))
        light.addcomponent(Light())
        
        cube1 = GameObject(Transform((0,1,0),scale=(10,1,2)), Cube(color=Color.white), BoxCollider(), Rigidbody(10000))
        cube1.rigidbody.usegravity = False

        
        cube2 = GameObject(Transform((12,3,0),scale=(10,1,2)), Cube(color=Color.white), BoxCollider(), Rigidbody(10000))
        cube2.rigidbody.usegravity = False
        
        sphere = GameObject(Transform((0,10,0)), Sphere(color=Color.green), SphereCollider(), Rigidbody(1), Qwe())
        sphere.addcomponent(Camera((0, 0, 20)))
        self.scene.addgameobjects(cube1, cube2, sphere)

if __name__ == "__main__":
    p = Platformer()
    p.mainloop()