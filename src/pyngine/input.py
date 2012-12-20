import pygame


class Input(object):
    """
    Class used to track all the input data
    of the current gameloop iteration
    """
    quitflag = False
    keys = {}
    mouse_visibility = True
    _up_buttons = (pygame.K_w, pygame.K_UP)
    _down_buttons = (pygame.K_s, pygame.K_DOWN)
    _left_buttons = (pygame.K_a, pygame.K_LEFT)
    _right_buttons = (pygame.K_d, pygame.K_RIGHT)
    
    @classmethod
    def update(cls):
        """
        Updates class information using the input event data
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cls.quitflag = True
            if event.type == pygame.KEYUP:
                cls.keys[event.key] = False
            if event.type == pygame.KEYDOWN:
                cls.keys[event.key] = True
                
    @classmethod
    def getkey(cls, key):
        """
        Returns whether a key is pressed or not
        
        Parameters
        ----------
        key : int
            Pygame key constant
        """
        try:
            return cls.keys[key]
        except KeyError:
            cls.keys[key] = False
            return False
        
    @classmethod
    def get_mouse_position(cls):
        """
        Returns the current position of the mouse
        """
        return pygame.mouse.get_pos()
    
    @classmethod
    def get_mouse_button(cls, index):
        """
        Returns whether a button of the mouse is pressed or not
        
        Parameters
        ----------
        index : int
            The index of the mouse button
        """
        return pygame.mouse.get_pressed()[index]
    
    @classmethod
    def get_mouse_visibility(cls):
        """
        Returns a boolean indicating whether the mouse is visible or not
        """
        return cls.mouse_visibility
    
    @classmethod
    def setmousevisibility(cls, boolean):
        """
        Sets the visibility of the mouse
        
        Parameters
        ----------
        boolean : bool
        """
        cls.mouse_visibility = boolean
        pygame.mouse.set_visible(boolean)
    
    @classmethod
    def get_horizontal_axis(cls):
        """
        Returns the input direction of the horizontal axis
        """
        if any(Input.getkey(x) for x in cls._left_buttons):
            return -1
        elif any(Input.getkey(x) for x in cls._right_buttons):
            return 1
        else:
            return 0
    
    @classmethod
    def get_vertical_axis(cls):
        """
        Returns the input direction of the vertical axis
        """
        if any(Input.getkey(x) for x in cls._down_buttons):
            return -1
        elif any(Input.getkey(x) for x in cls._up_buttons):
            return 1
        else:
            return 0
