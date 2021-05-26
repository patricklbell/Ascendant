import pygame, copy

class Camera():
    """ Manages position of camera, whoose position offsets all rendering.
    
        Args:
            position (pygame.Vector2): Optional initial position of camera.
            max_move_speed (int): Maximum speed camera moves to focus, scaled by relative position of focus.
            min_move_speed (int): Minimum speed camera moves to focus, avoid slow drift when focus is close to center.
            max_offset (pygame.Vector2): Maximum fractional offset of camera from focus before position is corrected
            contraints_max (pygame.Vector2): Smallest allowed value of camera position
            contraints_min (pygame.Vector2): Largest allowed value of camera position
            scale (tuple): x, y components by the surface size is scaled by
    """
    def __init__(self, position=pygame.Vector2(0,0), max_move_speed=10, min_move_speed=1, max_offset=pygame.Vector2(0.1, 0.1), contraints_max=pygame.Vector2(2880, 300), contraints_min=pygame.Vector2(0, 0), scale=(1,1)):
        self.scale = scale
        self.position = position
        self.contraints_max = contraints_max
        self.contraints_min = contraints_min
        self.max_speed = max_move_speed
        self.min_speed = min_move_speed
        self.max_offset = max_offset
    def update_position(self, focus_position, surface):
        """ Moves camera to keep focus in frame.
        Returns True if camera moved and False otherwise

        Args:
            focus_position (pygame.Vector2): Level space coordinates of focus position (required).
            surface (pygame.Surface): Surface which camera space will be rendered to, scaled by camera scale (required).
        """
        # Save previous position to determine if camera moved
        previous_position = copy.deepcopy(self.position)

        # Get relative position and level space size
        focus_position = focus_position + self.position
        win_width,win_height = surface.get_width()/self.scale[0], surface.get_height()/self.scale[1]
        
        # Test if focus lies outside maximum x offset on each side
        if focus_position.x > win_width * (0.5+self.max_offset.x):
            # Focus lies to right, determine by what fraction focus is off from max offset
            deviation = focus_position.x / ( win_width*(0.5+self.max_offset.x) ) - 1
            # Correct position towards left, scaling movement speed by deviation and limiting to max and min speeds 
            self.position.x = max(self.position.x - max(self.max_speed*deviation, self.min_speed), -self.contraints_max.x+win_width)
        if focus_position.x < win_width * (0.5-self.max_offset.x):
            # Focus lies to left, determine by what fraction focus is off from max offset
            deviation = 1 - focus_position.x / ( win_width*(0.5-self.max_offset.x) )
            # Correct position towards right, scaling movement speed by deviation and limiting to max and min speeds
            self.position.x = min(self.position.x + max(self.max_speed*deviation, self.min_speed), -self.contraints_min.x)
        
        # Peform same procedure on y coordinates
        if focus_position.y > win_height * (0.5+self.max_offset.y):
            deviation = focus_position.y / ( win_height*(0.5+self.max_offset.y) ) - 1
            self.position.y = max(self.position.y - max(self.max_speed*deviation, self.min_speed), -self.contraints_max.y+win_height)
        if focus_position.y < win_height * (0.5-self.max_offset.y):
            deviation = 1 - focus_position.y / ( win_height*(0.5-self.max_offset.y) )
            self.position.y = min(self.position.y + max(self.max_speed*deviation, self.min_speed), -self.contraints_min.y)

        # Return true if position changed
        return not previous_position == self.position

    def set_position(self, focus_position, surface):
        """ Directly sets camera positions as long as focus position lies in camera's constraints

        Args:
            focus_position (pygame.Vector2): Level space coordinates of focus position (required).
            surface (pygame.Surface): Surface which camera space will be rendered to, scaled by camera scale (required).
        """
        # Scale surface size to level space
        win_width,win_height = surface.get_width()/self.scale[0], surface.get_height()/self.scale[1]
        
        # Correct for x and y offsets without accounting for speed
        new_x = -focus_position.x + 0.5*win_width
        self.position.x = min(max(new_x, -self.contraints_max.x+win_width), -self.contraints_min.x)

        new_y = -focus_position.y + 0.5*win_height
        self.position.y = min(max(new_y, -self.contraints_max.y+win_height), -self.contraints_min.y)