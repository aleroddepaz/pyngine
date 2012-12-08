import ode



class PhysicsEngineError(Exception):
    """
    Class for errors in PhysicsEngine methods
    """
    def __init__(self, msg):
        Exception.__init__(self, msg)


class PhysicsEngine(object):
    
    world = ode.World()
    space = ode.Space()
    contactgroup = ode.JointGroup()
    
    @classmethod
    def start(cls, gravity=(0, -9.8, 0), erp=.8, cfm=1e-5):
        cls.world = ode.World()
        cls.world.setGravity(gravity)
        cls.world.setERP(erp)
        cls.world.setCFM(cfm)
        cls.space = ode.Space()
        cls.contactgroup = ode.JointGroup()
        
    @classmethod
    def step(cls, step):
        cls.world.step(step)
        cls.contactgroup.empty()
        
    @classmethod
    def collide(cls):
        cls.space.collide(None, cls._collidecallback)
        
    @classmethod
    def _collidecallback(cls, args, geom1, geom2):
        go1 = geom1.gameobject
        go2 = geom2.gameobject
        go1.oncollision(go2)
        go2.oncollision(go1)
        for contact in ode.collide(geom1, geom2):
            contact.setBounce(0)
            contact.setMu(10000)
            j = ode.ContactJoint(cls.world, cls.contactgroup, contact)
            j.attach(geom1.getBody(), geom2.getBody())
            
    @classmethod
    def createbody(cls):
        return ode.Body(cls.world)
    
    @classmethod
    def createmass(cls):
        return ode.Mass()
    
    @classmethod
    def creategeom(cls, geomtype, args):
        geomtype = "Geom" + geomtype
        try:
            return ode.__dict__[geomtype](cls.space, *args)
        except:
            raise PhysicsEngineError("Invalid Geom type: %s "
                                     "is not defined in `ode'" % geomtype)
