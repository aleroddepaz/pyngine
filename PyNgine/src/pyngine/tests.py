import unittest
from pyngine import * # @UnusedWildImport


class ExampleComponent(Component):
    def __init__(self):
        Component.__init__(self)
        self.started = False
        self.updates = 0
    def start(self):
        self.started = True
    def update(self):
        self.updates += 1


class TestComponent(unittest.TestCase):
    def setUp(self):
        self.component = ExampleComponent()
        self.gameobject = GameObject(Transform())
    def testStart1(self):
        self.gameobject.addcomponent(self.component)
        assert self.component.gameobject is self.gameobject
    def testStart2(self):
        self.gameobject.addcomponent(self.component)
        assert self.component.started
    def testUpdate(self):
        self.gameobject.addcomponent(self.component)
        self.gameobject.update()
        assert self.component.updates == 1


class TestTransform(unittest.TestCase):
    def setUp(self):
        self.transform = Transform(position=(0,0,0))
    def testMove(self):
        self.transform.move(movement=(1,1,1))
        assert self.transform.position == (1,1,1)


class TestCollider(unittest.TestCase):
    def setUp(self):
        self.collider = BoxCollider()
        self.gameobject = GameObject(Transform((0, 0, 0)))
    def tearDown(self):
        PhysicsEngine.start()
    def testStart1(self):
        self.gameobject.addcomponent(self.collider)
        assert self.collider.geom.placeable() == True
    def testStart2(self):
        self.gameobject.addcomponent(self.collider)
        assert self.collider.geom.isEnabled() == 1
    def testStart3(self):
        self.gameobject.addcomponent(self.collider)
        assert self.collider.geom.getBody() != None
    def testStart4(self):
        self.gameobject.addcomponent(self.collider)
        assert self.collider.geom.getBody().isEnabled() == 0
    def testStart5(self):
        self.gameobject.addcomponent(self.collider)
        self.gameobject.addcomponent(Rigidbody(1))
        assert self.collider.geom.getBody().isEnabled() == 1
    def testUpdate1(self):
        self.gameobject.addcomponent(self.collider)
        position_pre = self.gameobject.transform.position
        PhysicsEngine.step(1)
        assert self.gameobject.transform.position == position_pre
    def testUpdate2(self):
        self.gameobject.addcomponent(self.collider)
        self.gameobject.addcomponent(Rigidbody(1))
        position_pre = self.gameobject.transform.position
        PhysicsEngine.step(1)
        assert self.gameobject.transform.position != position_pre
    def testUpdate3(self):
        self.gameobject.addcomponent(self.collider)
        self.gameobject.addcomponent(Rigidbody(1))
        other = GameObject(Transform((0, -2, 0)), BoxCollider())
        position_pre = other.transform.position
        PhysicsEngine.step(1)
        assert other.transform.position == position_pre
    def testUpdate4(self):
        self.gameobject.addcomponent(self.collider)
        self.gameobject.addcomponent(Rigidbody(1))
        other = GameObject(Transform((0, -2, 0)), BoxCollider())
        PhysicsEngine.step(1)
        assert other.transform.position[1] < self.gameobject.transform.position[1]


class TestGameObject(unittest.TestCase):
    def setUp(self):
        self.transform = Transform(position=(0,0,0))
        self.gameobject = GameObject(self.transform)
    def tearDown(self):
        pass
    def testAddcomponent1(self):
        newtransform = Transform((1,1,1))
        self.gameobject.addcomponent(newtransform)
        assert self.gameobject.transform is newtransform
    def testAddcomponent2(self):
        newtransform = Transform((1,1,1))
        self.gameobject.addcomponent(newtransform)
        assert self.transform.gameobject == None
    def testAddcomponent3(self):
        component = ExampleComponent()
        self.gameobject.addcomponent(component)
        assert self.gameobject is component.gameobject
    def testAddcomponent4(self):
        component = ExampleComponent()
        self.gameobject.addcomponent(component)
        assert self.transform is component.transform


if __name__ == "__main__":
    unittest.main()
