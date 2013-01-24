from pyngine import * # @UnusedWildImport
from threading import Timer


class PlayerMovement(Component):
    def start(self):
        self.movementspeed = 10
        self.rotationspeed = 5
        self.jumpforce = 200
        self.canjump = False
    def update(self):
        transform = self.transform
        translatevalue = Input.getverticalaxis() * self.movementspeed * Game.delta
        rotationvalue = Input.gethorizontalaxis() * self.rotationspeed * Game.delta
        transform.translate(transform.forward * translatevalue)
        transform.rotate(Vector3D.up, rotationvalue)
        if Input.getkey(pygame.K_SPACE) and self.canjump:
            self.canjump = False
            self.rigidbody.addforce((0,self.jumpforce,0))
    def oncollision(self, other):
        self.canjump = True


class Shooter(Component):
    def start(self):
        self.shootforce = 100
        self.canshoot = False
        self.newbullethandler()
    def newbullethandler(self):
        self.canshoot = True
        self.timer = Timer(1., self.newbullethandler)
        self.timer.start()
    def update(self):
        if Input.getkey(pygame.K_q) and self.canshoot:
            self.canshoot = False
            position = self.transform.position + self.transform.forward * 1
            bullet = GameObject(Transform(position, scale=(.5,.5,.5)),
                                Sphere(Color.green), SphereCollider(), Rigidbody(1))
            bullet.tag = 'Bullet'
            bullet.rigidbody.addforce(self.transform.forward * self.shootforce)


class EnemyBehaviour(Component):
    def oncollision(self, other):
        if other.tag == 'Bullet':
            GameObject.destroy(self.gameobject)


class Platform(GameObject):
    def __init__(self, pos, size):
        GameObject.__init__(self, Transform(position=pos, scale=size),
                            Cube(color=Color.white), BoxCollider())


class Enemy(GameObject):
    def __init__(self, pos):
        GameObject.__init__(self, Transform(position=pos), Rigidbody(1),
                            Cube(color=Color.red), BoxCollider(), EnemyBehaviour())


class Platformer(Game):
    def __init__(self):
        Game.__init__(self)
        GameObject(Transform(position=(0,5,-5)), Light())
        Platform(pos=(0, 0 ,0), size=(20, 1, 20))
        Platform(pos=(11.5, 2, 0), size=(10, 1, 5))
        Platform(pos=(-12, 2, 0), size=(10, 1, 5))
        GameObject(Transform((0, 7, 0)), Cube(color=Color.green),
                   BoxCollider(), Rigidbody(1), Camera((0, 2, 20)),
                   PlayerMovement(), Shooter())
        enemypositions = [(3, 3, 3), (-3, 3, -1), (-8, 5, 0), (7, 5, 1)]
        for position in enemypositions:
            Enemy(pos=position)


if __name__ == "__main__":
    p = Platformer()
    p.mainloop()
