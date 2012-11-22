import pygame

class Game(object):
    def __init__(self):
        pygame.init()
        self.isactive = True
    def mainloop(self):
        while self.isactive:
            pass #do stuff

class GameObject(object):
    def __init__(self):
        self.position = [0,0,0]
        self.components = []
    def addcomponent(self, component):
        self.components.append(component)
    def removecomponent(self, component):
        self.components.remove(component)
    def handlemessage(self, string, data=None):
        result = None
        for component in self.components:
            result = component.handlemessage(string, data)
            if result != None: break
        return result

class Component(object):
    def __init__(self):
        pass
    def start(self):
        pass
    def update(self):
        pass
