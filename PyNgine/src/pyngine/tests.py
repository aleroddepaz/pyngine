import unittest
from pyngine.core import * # @UnusedWildImport


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
    def tearDown(self):
        pass
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
    def tearDown(self):
        pass
    def testMove(self):
        self.transform.move(movement=(1,1,1))
        assert self.transform.position == (1,1,1)


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
