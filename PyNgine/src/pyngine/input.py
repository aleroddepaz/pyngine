import pygame


class Input(object):
    quitflag = False
    keys = {}
    mousevisibility = True
    @classmethod
    def update(cls):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cls.quitflag = True
            if event.type == pygame.KEYUP:
                cls.keys[event.key] = False
            if event.type == pygame.KEYDOWN:
                cls.keys[event.key] = True
    @classmethod
    def getkey(cls, key):
        try:
            return cls.keys[key]
        except KeyError:
            cls.keys[key] = False
            return False
    @classmethod
    def getmouseposition(cls):
        return pygame.mouse.get_pos()
    @classmethod
    def getmousebutton(cls, index):
        return pygame.mouse.get_pressed()[index]
    @classmethod
    def getmousevisibility(cls):
        return cls.mousevisibility
    @classmethod
    def setmousevisibility(cls, boolean):
        cls.mousevisibility = boolean
        pygame.mouse.set_visible(boolean)
