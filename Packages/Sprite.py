import pygame, json, copy

# For debugging
from Packages import Settings

class ImageSprite():
    """ """
    def __init__(self, image_filename=None,scale=None):
        self.hidden=False
        if not image_filename == None:
            try:
                self.image = pygame.image.load(image_filename).convert_alpha()
            except:
                print("Invalid sprite image: ", image_filename)

        if not scale == None:
            self.image = pygame.transform.scale(self.image, (int(scale[0]*self.image.get_width()), int(scale[1]*self.image.get_height())))
    
    def render(self, surface, position=pygame.Vector2(0,0), size=None):
        """

        :param surface: 
        :param position:  (Default value = pygame.Vector2(0)
        :param 0): 
        :param size:  (Default value = None)

        """
        if not self.hidden:
            if size == None: 
                return [surface.blit(self.image, position)]
            else:
                return [surface.blit(self.image, position, area=size)]
    def hide(self):
        """ """
        self.hidden = True
    def show(self):
        """ """
        self.hidden = False
    # https://stackoverflow.com/questions/57225611/how-to-deepcopy-object-which-contains-pygame-surface
    def copy(self):
        """ """
        copyobj = ImageSprite()
        for name, attr in self.__dict__.items():
            if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
                copyobj.__dict__[name] = attr.copy()
            else:
                copyobj.__dict__[name] = copy.deepcopy(attr)
        return copyobj

class ImageSpriteSheet():
    """ """
    def __init__(self, spritesheet_json_filename=None, spritesheet_scale=(1,1)):
        self.images = {}
        if not spritesheet_json_filename == None:
            self.load_spritesheet(spritesheet_json_filename, spritesheet_scale)

    def load_spritesheet(self, spritesheet_json_filename, scale):
        """

        :param spritesheet_json_filename: 
        :param scale: 

        """
        with open(spritesheet_json_filename) as json_file:
            json_data = json.load(json_file)

        try:
            self.spritesheet_image = pygame.image.load(Settings.SRC_DIRECTORY+json_data["filename"]).convert_alpha()
        except:
            print('Unable to load spritesheet image:', json_data["filename"])

        for name in json_data["images"]:
            x_offset = json_data["images"][name]["x_offset"]
            y_offset = json_data["images"][name]["y_offset"]
            x_size = json_data["images"][name]["x_size"]
            y_size = json_data["images"][name]["y_size"]

            rect = pygame.Rect((x_offset, y_offset, x_size, y_size))
            image = pygame.Surface(rect.size, pygame.SRCALPHA).convert_alpha()
            image.blit(self.spritesheet_image, (0, 0), rect)
            image = pygame.transform.scale(image, (int(x_size*scale[0]), int(y_size*scale[1])))

            self.images[name] = image

    def render(self, surface, image_name, position=pygame.Vector2(0,0), size=None):
        """

        :param surface: 
        :param image_name: 
        :param position:  (Default value = pygame.Vector2(0)
        :param 0): 
        :param size:  (Default value = None)

        """
        if size == None: 
            return [surface.blit(self.images[image_name], position)]
        else:
            return [surface.blit(self.images[image_name], position, area=size)]

    # https://stackoverflow.com/questions/57225611/how-to-deepcopy-object-which-contains-pygame-surface
    def copy(self):
        """ """
        copyobj = ImageSpriteSheet()
        for name, attr in self.__dict__.items():
            if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
                copyobj.__dict__[name] = attr.copy()
            else:
                copyobj.__dict__[name] = copy.deepcopy(attr)
        return copyobj


class AnimatedSprite():
    """ """
    def __init__(self, position = pygame.Vector2(0, 0), spritesheet_json_filename = None, spritesheet_scale=(1,1), calculate_flip=False, calculate_white=False, *args, **kwargs):
        self.hidden = False
        self.position = position
        self.animation_finished = False
        self.animation_name = ""
        self.animation_time = 0
        self.animation_index = 0
        self.animation_playing = False
        self.animation_looping = False
        self.on_animation_end = lambda self: 1
        self.on_animation_interrupt = lambda self: 1
        self.animations_data = None
        self.spritesheet_image = None
        self.flipX = False
        self.is_white = False
        self.frame_num = 0
        self.speed = 1
        self.frame_image = None

        if not spritesheet_json_filename == None:
            self.load_spritesheet(spritesheet_json_filename, spritesheet_scale, calculate_flip=calculate_flip, calculate_white=calculate_white)
    def hide(self):
        """ """
        self.hidden = True
    def show(self):
        """ """
        self.hidden = False
    def update_animation(self, delta):
        """

        :param delta: 

        """
        current_animation = self.animations_data[self.animation_index]

        # Advance frame if animation is playing
        self.animation_time += delta*self.speed
        if self.animation_playing:
            self.frame_num = int((self.animation_time / current_animation["time"]) * (current_animation["frame_length"] - 1))
            if self.frame_num > current_animation["frame_length"] - 1:
                if self.animation_looping:
                    self.frame_num = 0

                    self.animation_time = 0
                else:
                    self.frame_num = current_animation["frame_length"] - 1

                    self.animation_playing = False
                    self.animation_finished = True
                    self.on_animation_end(self)
        
        frame_type = ["frames", "frames_flipped", "frames_white", "frames_white_flipped"][self.flipX + 2*self.is_white]
        self.frame_image = current_animation[frame_type][self.frame_num]

    def render(self, surface, offset=pygame.Vector2(0,0), size=None, delta=None):
        """

        :param surface: 
        :param offset:  (Default value = pygame.Vector2(0)
        :param 0): 
        :param size:  (Default value = None)
        :param delta:  (Default value = None)

        """
        if not self.hidden:
            if not delta == None:
                self.update_animation(delta)

            # Check if sprite needs to be drawn
            if not self.frame_image == None:
                relative_position = self.position + offset
                if relative_position.x + self.frame_image.get_width() > 0 and relative_position.x <= Settings.RESOLUTION[0] and relative_position.y + self.frame_image.get_height() > 0 and relative_position.y <= Settings.RESOLUTION[1]:
                    if size == None: 
                        return [surface.blit(self.frame_image, self.position + offset)]
                    else:
                        return [surface.blit(self.frame_image, self.position + offset, size)]
        
        return []

    def load_spritesheet(self, spritesheet_json_filename, scale=(1, 1), calculate_flip=False, calculate_white=False):
        """

        :param spritesheet_json_filename: 
        :param scale:  (Default value = (1)
        :param 1): 
        :param calculate_flip:  (Default value = False)
        :param calculate_white:  (Default value = False)

        """
        "Loads set of animations from a spritesheet (png) and json"

        self.animations_data = []

        with open(spritesheet_json_filename) as json_file:
            json_data = json.load(json_file)

        try:
            self.spritesheet_image = pygame.image.load(Settings.SRC_DIRECTORY+json_data["filename"]).convert_alpha()
        except:
            print('Unable to load spritesheet image:', json_data["filename"])

        for animation in json_data["animations"]:
            x_init_offset = animation["x_init_offset"]
            y_init_offset = animation["y_init_offset"]
            x_size = animation["x_size"]
            y_size = animation["y_size"]
            x_offset = animation["x_offset"]
            y_offset = animation["y_offset"]
            time = animation["time"]
            frame_length = animation["frame_length"]

            x = x_init_offset
            y = y_init_offset

            animation_data = {"name": animation["name"], "time": time, "frame_length": frame_length, "frames":[]}
            if calculate_flip:
                animation_data["frames_flipped"] = []
            if calculate_white:
                animation_data["frames_white"] = []
                if calculate_flip:
                    animation_data["frames_white_flipped"] = []

            for _ in range(frame_length):
                rect = pygame.Rect((x, y, x_size, y_size))
                image = pygame.Surface(rect.size, pygame.SRCALPHA).convert_alpha()
                image.blit(self.spritesheet_image, (0, 0), rect)
                image = pygame.transform.scale(image, (int(x_size*scale[0]), int(y_size*scale[1])))

                x += x_offset
                y += y_offset
                animation_data["frames"].append(image)
                if calculate_flip:
                    animation_data["frames_flipped"].append(pygame.transform.flip(image, True, False))
                if calculate_white:
                    white_image = image.copy()
                    w, h = white_image.get_size()
                    for x_px in range(w):
                        for y_px in range(h):
                            if white_image.get_at((x_px, y_px)).a == 255:
                                white_image.set_at((x_px, y_px), pygame.Color(255,255,255))
                    animation_data["frames_white"].append(white_image)
                    if calculate_flip:
                        animation_data["frames_white_flipped"].append(pygame.transform.flip(white_image, True, False))
                    

            self.animations_data.append(animation_data)

    def play_animation(self, animation_name="", speed=1, animation_time=0, loop=False, on_animation_end = lambda self: 1, on_animation_interrupt = lambda self: 1):
        """

        :param animation_name:  (Default value = "")
        :param speed:  (Default value = 1)
        :param animation_time:  (Default value = 0)
        :param loop:  (Default value = False)
        :param on_animation_end:  (Default value = lambda self: 1)
        :param on_animation_interrupt:  (Default value = lambda self: 1)

        """
        self.on_animation_interrupt(self)
        self.on_animation_interrupt = on_animation_interrupt

        self.animation_index = 0
        self.frame_num = 0
        self.speed = speed
        self.animation_finished = False

        flag = True
        for i in range(len(self.animations_data)):
            if self.animations_data[i]["name"] == animation_name:
                self.animation_name = animation_name
                self.animation_index = i
                flag = False
        if flag and Settings.DEBUG:
            print(f"Animation {animation_name} not found")
        
        self.animation_time = animation_time
        self.animation_looping = loop
        self.animation_playing = True
        self.on_animation_end = on_animation_end

    def input(self):
        """ """
        pass
    
    # https://stackoverflow.com/questions/57225611/how-to-deepcopy-object-which-contains-pygame-surface
    def copy(self):
        """ """
        copyobj = AnimatedSprite()
        for name, attr in self.__dict__.items():
            if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
                copyobj.__dict__[name] = attr.copy()
            else:
                copyobj.__dict__[name] = copy.deepcopy(attr)
        return copyobj