import pygame



class Input(object):
    
    quitflag = False
    keys = {}
    mouse_visibility = True
    
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
        return cls.mouse_visibility
    
    @classmethod
    def setmousevisibility(cls, boolean):
        cls.mouse_visibility = boolean
        pygame.mouse.set_visible(boolean)
    
    @classmethod
    def gethorizontalaxis(cls):
        if Input.getkey(pygame.K_a) or Input.getkey(pygame.K_LEFT):
            return -1
        elif Input.getkey(pygame.K_d) or Input.getkey(pygame.K_RIGHT):
            return 1
        else:
            return 0
    
    @classmethod
    def getverticalaxis(cls):
        if Input.getkey(pygame.K_s) or Input.getkey(pygame.K_DOWN):
            return -1
        elif Input.getkey(pygame.K_w) or Input.getkey(pygame.K_UP):
            return 1
        else:
            return 0
