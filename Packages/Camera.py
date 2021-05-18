import pygame, copy

class Camera():
    """ """
    def __init__(self, position=pygame.Vector2(0,0), max_move_speed=10, min_move_speed=1, max_offset=pygame.Vector2(0.1, 0.1), contraints_max=pygame.Vector2(2880, 300), contraints_min=pygame.Vector2(0, 0), scale=(1,1)):
        """
        
        :param position: (Default value = pygame.Vector2(0,0))
        :param max_move_speed: (Default value = 10) pixels per update call
        :param min_move_speed: (Default value = 1) pixels per update call
        :param max_offset: (Default value = pygame.Vector2(0.1, 0.1)) float representing percentage screen size
        :param 
        """
        self.scale = scale
        self.position = position
        self.contraints_max = contraints_max
        self.contraints_min = contraints_min
        self.max_speed = max_move_speed
        self.min_speed = min_move_speed
        self.max_offset = max_offset
    def update_position(self, delta, focus_position, surface):
        """

        :param delta: 
        :param focus_position:
        :param surface: 
        :param focus_position: 

        """
        previous_position = copy.deepcopy(self.position)
        focus_position = focus_position + self.position
        win_width,win_height = surface.get_width()/self.scale[0], surface.get_height()/self.scale[1]
        
        if focus_position.x > win_width * (0.5+self.max_offset.x):
            deviation = ( focus_position.x - win_width*(0.5+self.max_offset.x) ) / ( win_width*(0.5-self.max_offset.x) )
            self.position.x = max(self.position.x - max(self.max_speed*deviation, self.min_speed), -self.contraints_max.x+win_width)
        if focus_position.x < win_width * (0.5-self.max_offset.x):
            deviation = ( (win_width*(0.5-self.max_offset.x) - focus_position.x) ) / ( win_width*(0.5-self.max_offset.x) )
            self.position.x = min(self.position.x + max(self.max_speed*deviation, self.min_speed), -self.contraints_min.x)
        
        if focus_position.y > win_height * (0.5+self.max_offset.y):
            deviation = ( focus_position.y - win_height*(0.5+self.max_offset.y) ) / ( win_height*(0.5-self.max_offset.y) )
            self.position.y = max(self.position.y - max(self.max_speed*deviation, self.min_speed), -self.contraints_max.y+win_height)
        if focus_position.y < win_height * (0.5-self.max_offset.y):
            deviation = ( (win_height*(0.5-self.max_offset.y) - focus_position.y) ) / ( win_height*(0.5-self.max_offset.y) )
            self.position.y = min(self.position.y + max(self.max_speed*deviation, self.min_speed), -self.contraints_min.y)

        return not previous_position == self.position

    def set_position(self, focus_position, surface):
        """

        :param focus_position: param surface:
        :param surface: 

        """
        win_width,win_height = surface.get_width()/self.scale[0], surface.get_height()/self.scale[1]
        
        new_x = -focus_position.x + 0.5*win_width
        self.position.x = min(max(new_x, -self.contraints_max.x+win_width), -self.contraints_min.x)

        new_y = -focus_position.y + 0.5*win_height
        self.position.y = min(max(new_y, -self.contraints_max.y+win_height), -self.contraints_min.y)