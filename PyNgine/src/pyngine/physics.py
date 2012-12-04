import ode


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
        cls.space.collide(None, cls.__collidecallback)
    @classmethod
    def __collidecallback(cls, args, geom1, geom2):
        go1 = geom1.gameobject
        go2 = geom2.gameobject
        go1.oncollision(go2)
        go2.oncollision(go1)
        for contact in ode.collide(geom1, geom2):
            contact.setBounce(0)
            contact.setMu(10000)
            if geom1.getBody().isEnabled() == 0: return
            if geom2.getBody().isEnabled() == 0: return
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
            print "Error in PhysicsEngine.creategeom!!"
