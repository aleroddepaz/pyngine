from pyngine import * # @UnusedWildImport


class PlayerMovement(Component):
    
    def start(self):
        self.speed = 5
        self.jumpforce = 200
        self.canjump = False
        
    def update(self):
        rigidbody = self.gameobject.rigidbody
        x = self.speed * Input.gethorizontalaxis()
        y = rigidbody.velocity[1]
        z = self.speed * Input.getverticalaxis()
        rigidbody.velocity = (x, y, z)
        if Input.getkey(pygame.K_SPACE) and self.canjump:
            self.canjump = False
            rigidbody.addforce((0,self.jumpforce,0))
                
    def oncollision(self, other):
        self.canjump = True


class Platform(GameObject):
    
    def __init__(self, pos, size):
        GameObject.__init__(self, Transform(position=pos, scale=size))
        self.addcomponents(Cube(color=Color.white), BoxCollider())
        

class Platformer(Game):
    
    def __init__(self):
        Game.__init__(self)
        light = GameObject(Transform((0,5,-5)))
        light.addcomponent(Light())
        platform1 = Platform(pos=(0, 0 ,0), size=(20, 1, 20))
        platform2 = Platform(pos=(11.5, 2, 0), size=(10, 1, 5))
        platform3 = Platform(pos=(-12, 4, 0), size=(10, 1, 5))
        sphere = GameObject(Transform((0, 7, 0)), Sphere(color=Color.green), SphereCollider(), Rigidbody(1))
        sphere.addcomponents(Camera((0, 2, 20)), PlayerMovement())
        woman = GameObject(Transform((4,4,0), scale=(.5,.5,.5)), Mesh('woman.obj'))
        self.scene.addgameobjects(light, platform1, platform2, platform3, sphere, woman)

if __name__ == "__main__":
    p = Platformer()
    p.mainloop()
