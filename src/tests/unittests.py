import unittest
from pyngine import * # @UnusedWildImport


# ==============================
# Test utils
# ==============================

class PhysicsSimulator(object):
    """
    Utility class for simulating physics steps
    """
    @classmethod
    def step(cls, time):
        for _ in xrange(time):
            PhysicsEngine.step(1./time)


class ExampleComponent(Component):
    
    def __init__(self):
        Component.__init__(self)
        self.started = False
        self.updates = 0
        
    def start(self):
        self.started = True
        
    def update(self):
        self.updates += 1



# ==============================
# Test Cases
# ==============================

class TestVector3D(unittest.TestCase):
    
    def setUp(self):
        self.vector = Vector3D(1, 1, 1)
    
    def testAdd(self):
        other = Vector3D(1, 2, 3)
        assert self.vector + other == Vector3D(2, 3, 4)
    
    def testSub(self):
        other = Vector3D(.5, .5, .5)
        assert self.vector - other == Vector3D(.5, .5, .5)
        
    def testMul(self):
        factor = 5
        assert self.vector * factor == Vector3D(5, 5, 5)


class TestQuaternion(unittest.TestCase):
    
    def setUp(self):
        self.quaternion = Quaternion(1, 0, 1, 0)
    
    def testConjugate(self):
        conjugate = self.quaternion.conjugate
        assert conjugate == (1, 0, -1, 0)


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
        self.transform = Transform(position=(0, 0, 0))
        self.child = Transform(position=(0, 1, 0))
        
    def testTranslate1(self):
        self.transform.translate(movement=(1, 1, 1))
        assert self.transform.position == (1, 1, 1)
    
    def testTranslate2(self):
        self.transform.addchild(self.child)
        self.transform.translate(movement=(1, 1, 1))
        assert self.child.position == (1, 2, 1)

    def testRotate(self):
        self.transform.rotate(Vector3D.up, math.pi)
        assert self.transform.rotation.round == (0, 0, 1, 0)
    
    def testAddChild(self):
        self.transform.addchild(self.child)
        assert self.child in self.transform


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
        PhysicsSimulator.step(60)
        assert self.gameobject.transform.position == position_pre
        
    def testUpdate2(self):
        self.gameobject.addcomponent(self.collider)
        self.gameobject.addcomponent(Rigidbody(1))
        position_pre = self.gameobject.transform.position
        PhysicsSimulator.step(60)
        assert self.gameobject.transform.position != position_pre
        
    def testUpdate3(self):
        self.gameobject.addcomponent(self.collider)
        self.gameobject.addcomponent(Rigidbody(1))
        other = GameObject(Transform((0, -2, 0)), BoxCollider())
        position_pre = other.transform.position
        PhysicsSimulator.step(60)
        assert other.transform.position == position_pre
        
    def testUpdate4(self):
        self.gameobject.addcomponent(self.collider)
        other = GameObject(Transform((0, 5, 0)),
                           BoxCollider(), Rigidbody(1))
        PhysicsSimulator.step(60)
        ygameobject = self.gameobject.transform.position.y
        yother = other.transform.position.y
        assert ygameobject < yother

    def testUpdate5(self):
        self.gameobject.addcomponent(self.collider)
        position_pre = self.gameobject.transform.position
        other = GameObject(Transform((0, 5, 0)), #@UnusedVariable
                           BoxCollider(), Rigidbody(1)) 
        PhysicsSimulator.step(60)
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
