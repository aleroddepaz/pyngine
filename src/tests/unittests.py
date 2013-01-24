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
        
    def testTranslate(self):
        self.transform.translate(movement=(1,1,1))
        assert self.transform.position == (1,1,1)

    def testRotate(self):
        self.transform.rotate([0,1,0], math.pi)
        quaternion = tuple(map(math.floor, self.transform.rotation))
        assert quaternion == (0,0,1,0)


class TestCollider(unittest.TestCase):
    
    def setUp(self):
        self.collider = BoxCollider()
        self.gameobject = GameObject(Transform((0,0,0)))
        
    def tearDown(self):
        PhysicsEngine.start()
        
    def testStart1(self):
        self.gameobject.addcomponent(self.collider)
        assert self.collider._geom.placeable() == True
        
    def testStart2(self):
        self.gameobject.addcomponent(self.collider)
        assert self.collider._geom.isEnabled() == 1
        
    def testStart3(self):
        self.gameobject.addcomponent(self.collider)
        assert self.collider._geom.getBody() == None
        
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
        for _ in xrange(60): PhysicsEngine.step(1./60)
        assert other.transform.position == position_pre
        
    def testUpdate4(self):
        self.gameobject.addcomponent(self.collider)
        other = GameObject(Transform((0, 5, 0)),
                           BoxCollider(), Rigidbody(1))
        for _ in xrange(60): PhysicsEngine.step(1./60)
        ygameobject = self.gameobject.transform.position.y
        yother = other.transform.position.y
        assert ygameobject < yother

    def testUpdate5(self):
        self.gameobject.addcomponent(self.collider)
        position_pre = self.gameobject.transform.position
        other = GameObject(Transform((0, 5, 0)), #@UnusedVariable
                           BoxCollider(), Rigidbody(1)) 
        for _ in xrange(60): PhysicsEngine.step(1./60)
        assert self.gameobject.transform.position == position_pre


class TestGameObject(unittest.TestCase):
    
    def setUp(self):
        self.transform = Transform(position=(0,0,0))
        self.gameobject = GameObject(self.transform)
        
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
