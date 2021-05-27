import pygame, json, copy

# For debugging
from Packages import Settings

class ImageSprite():
    """ General class for loading and rendering an image.
    
    Args:
        image_filename (str): File path of image to be loaded.
        scale (tuple): x, y componenets to scale image by.
    """
    def __init__(self, image_filename=None,scale=None):
        # Make image hideable
        self.hidden=False

        # Attempt to load file
        if not image_filename == None:
            try:
                self.image = pygame.image.load(image_filename).convert_alpha()
            except FileNotFoundError:
                print("Invalid sprite image: ", image_filename)
        # Scale each component
        if not scale == None:
            self.image = pygame.transform.scale(self.image, (int(scale[0]*self.image.get_width()), int(scale[1]*self.image.get_height())))
    
    def render(self, surface, position=pygame.Vector2(0,0), size=None):
        """ Draws image sprite to surface at position and optionally size.
        Returns list of dirty rects which have been rendered to.

        Args:
            surface (pygame.Surface): Surface to render to (required).
            position (pygame.Vector2): Position to render image at
            size (tuple): x, y integer pixel size to render to surface.
        """
        # Dont render if hidden
        if not self.hidden:
            # Apply optional size and return dirty rect
            if size == None: 
                return [surface.blit(self.image, position)]
            else:
                return [surface.blit(self.image, position, area=size)]
    def hide(self):
        """ Hides image so it isnt rendered """
        self.hidden = True
    def show(self):
        """ Shows image so it is rendered """
        self.hidden = False
    # https://stackoverflow.com/questions/57225611/how-to-deepcopy-object-which-contains-pygame-surface
    def copy(self):
        """ Standard copy constructor for complex objects """
        copyobj = ImageSprite()
        for name, attr in self.__dict__.items():
            if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
                copyobj.__dict__[name] = attr.copy()
            else:
                copyobj.__dict__[name] = copy.deepcopy(attr)
        return copyobj

class ImageSpriteSheet():
    """ General class for loading a sprite sheet from file and displaying specific frames 
    
    Args:
        spritesheet_json_filename (str): File path of json which describes frames to be loaded.
        spritesheet_scale (tuple): x, y componenets to scale spritesheet by.
    """
    def __init__(self, spritesheet_json_filename=None, spritesheet_scale=(1,1)):
        self.images = {}
        # Load if json file given
        if not spritesheet_json_filename == None:
            self.load_spritesheet(spritesheet_json_filename, spritesheet_scale)

    def load_spritesheet(self, spritesheet_json_filename, scale):
        """ Loads spritesheet image into memory from json file.

        Args:
            spritesheet_json_filename (str): File path of json which describes frames to be loaded.
            scale (tuple): x, y componenets to scale spritesheet by.
        """
        # Load json
        with open(spritesheet_json_filename) as json_file:
            json_data = json.load(json_file)

        # Attempt to load image given by json
        try:
            self.spritesheet_image = pygame.image.load(Settings.SRC_DIRECTORY+json_data["filename"]).convert_alpha()
        except FileNotFoundError:
            print('Unable to load spritesheet image:', json_data["filename"])

        # Splite spritesheet into each image
        for name in json_data["images"]:
            x_offset = json_data["images"][name]["x_offset"]
            y_offset = json_data["images"][name]["y_offset"]
            x_size = json_data["images"][name]["x_size"]
            y_size = json_data["images"][name]["y_size"]
            
            # Create new surface of correct size
            rect = pygame.Rect((x_offset, y_offset, x_size, y_size))
            image = pygame.Surface(rect.size, pygame.SRCALPHA).convert_alpha()

            # Crop spritesheet onto image and scale
            image.blit(self.spritesheet_image, (0, 0), rect)
            image = pygame.transform.scale(image, (int(x_size*scale[0]), int(y_size*scale[1])))

            # Save new image under correct name
            self.images[name] = image

    def render(self, surface, image_name, position=pygame.Vector2(0,0), size=None):
        """ Draws specific image from spritesheet to surface at position and optionally with size.
        Returns list of dirty rects which have been rendered to.

        Args:
            surface (pygame.Surface): Surface to render to (required).
            position (pygame.Vector2): Position to render image at
            size (tuple): x, y integer pixel size to render to surface.

        """
        # Draw image from dictionary with optional size
        if size == None: 
            return [surface.blit(self.images[image_name], position)]
        else:
            return [surface.blit(self.images[image_name], position, area=size)]

    # https://stackoverflow.com/questions/57225611/how-to-deepcopy-object-which-contains-pygame-surface
    def copy(self):
        """ Standard copy constructor for complex objects """
        copyobj = ImageSpriteSheet()
        for name, attr in self.__dict__.items():
            if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
                copyobj.__dict__[name] = attr.copy()
            else:
                copyobj.__dict__[name] = copy.deepcopy(attr)
        return copyobj


class AnimatedSprite():
    """ General class for handling loading, rendering and updating animations from a spritesheet.
    
    Args:
        position (pygame.Vector2): Position of animation within surface its rendered to.
        spritesheet_json_filename (str): Path of json file describing animations for spritesheet.
        spritesheet_scale (tuple): x, y components to scale animation sizes by.
        calculate_flip (bool): Flag which determines whether a flipped copy of animations are stored.
        calculate_white (bool): Flag which determines whether a white copy of animations are stored.
    """
    def __init__(self, position = pygame.Vector2(0, 0), spritesheet_json_filename = None, spritesheet_scale=(1,1), calculate_flip=False, calculate_white=False, *args, **kwargs):
        # Setup state
        self.hidden = False
        self.position = position
        self.animation_finished = False
        self.animation_name = ""
        self.animation_time = 0
        self.animation_index = 0
        self.animation_playing = False
        self.animation_looping = False
        # User specified functions which self is passed to
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
        """ Hides image so it isnt rendered """
        self.hidden = True
    def show(self):
        """ Shows image so it is rendered """
        self.hidden = False
    def update_animation(self, delta):
        """ Update frame position in current animation, if one is playing.

        Args:
            delta (float): Seconds since last update call.
        """
        # Set current frame correctly
        current_animation = self.animations_data[self.animation_index]

        # Advance frame if animation is playing
        self.animation_time += delta*self.speed
        if self.animation_playing:
            # Scale proportion of animation completed to a frame number
            self.frame_num = int((self.animation_time / current_animation["time"]) * (current_animation["frame_length"] - 1))

            # Handle completing and looping animations
            if self.frame_num > current_animation["frame_length"] - 1:
                if self.animation_looping:
                    self.frame_num = 0
                    self.animation_time = 0
                else:
                    self.frame_num = current_animation["frame_length"] - 1

                    self.animation_playing = False
                    self.animation_finished = True
                    self.on_animation_end(self)
        # Get type of frame from 4 permutations and set correct frame
        frame_type = ["frames", "frames_flipped", "frames_white", "frames_white_flipped"][self.flipX + 2*self.is_white]
        self.frame_image = current_animation[frame_type][self.frame_num]

    def render(self, surface, offset=pygame.Vector2(0,0), size=None, delta=None):
        """ Draw current frame of animation to surface and optionally update animation if delta is given.
        Returns list of dirty rects which have been rendered to.

        Args:
            surface (pygame.Surface): Surface to render animation to (required).
            offset (pygame.Vector2): Offset between position of animation and render position.
            size (tuple): x, y integer components of size of rendered frames.
            delta (float): Seconds since last animation update. 
        """
        if not self.hidden:
            # Update animation if delta is given
            if not delta == None:
                self.update_animation(delta)

            # Check if sprite needs to be drawn
            if not self.frame_image == None:
                relative_position = self.position + offset
                # Only draw if frame lies within screen
                if relative_position.x + self.frame_image.get_width() > 0 and relative_position.x <= Settings.RESOLUTION[0] and relative_position.y + self.frame_image.get_height() > 0 and relative_position.y <= Settings.RESOLUTION[1]:
                    if size == None: 
                        return [surface.blit(self.frame_image, self.position + offset)]
                    else:
                        return [surface.blit(self.frame_image, self.position + offset, size)]
        
        return []

    def load_spritesheet(self, spritesheet_json_filename, scale=(1, 1), calculate_flip=False, calculate_white=False):
        """ Loads spritesheet animation into memory from json file describing animations.

        Args:
            spritesheet_json_filename (str): File path of json which describes frames to be loaded (required).
            scale (tuple): x, y componenets to scale spritesheet by.
            calculate_flip (bool): Flag which determines whether a flipped copy of animations are stored.
            calculate_white (bool): Flag which determines whether a white copy of animations are stored.
        """

        self.animations_data = []

        with open(spritesheet_json_filename) as json_file:
            json_data = json.load(json_file)

        # Attempt to load image given by json file with transparency
        try:
            self.spritesheet_image = pygame.image.load(Settings.SRC_DIRECTORY+json_data["filename"]).convert_alpha()
        except:
            print('Unable to load spritesheet image:', json_data["filename"])

        # Load each animation
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

            # Setup animation data dictionary
            animation_data = {"name": animation["name"], "time": time, "frame_length": frame_length, "frames":[]}

            # Add each extra type of frame as necessary
            if calculate_flip:
                animation_data["frames_flipped"] = []
            if calculate_white:
                animation_data["frames_white"] = []
                if calculate_flip:
                    animation_data["frames_white_flipped"] = []

            # Load each frame for animation
            for _ in range(frame_length):
                # Create new transparent surface of correct size
                rect = pygame.Rect((x, y, x_size, y_size))
                image = pygame.Surface(rect.size, pygame.SRCALPHA).convert_alpha()

                # Crop spritesheet onto image and scale
                image.blit(self.spritesheet_image, (0, 0), rect)
                image = pygame.transform.scale(image, (int(x_size*scale[0]), int(y_size*scale[1])))

                # Save image as frame and advance x, y offset in spritesheet
                x += x_offset
                y += y_offset
                animation_data["frames"].append(image)
                # Create other types of frames
                if calculate_flip:
                    # Flip about vertical axis
                    animation_data["frames_flipped"].append(pygame.transform.flip(image, True, False))
                if calculate_white:
                    white_image = image.copy()
                    w, h = white_image.get_size()
                    # Set all non transparent pixels within image to white
                    for x_px in range(w):
                        for y_px in range(h):
                            if white_image.get_at((x_px, y_px)).a == 255:
                                white_image.set_at((x_px, y_px), pygame.Color(255,255,255))
                    # Add white frame and calculate flipped white
                    animation_data["frames_white"].append(white_image)
                    if calculate_flip:
                        # Flip about vertical axis
                        animation_data["frames_white_flipped"].append(pygame.transform.flip(white_image, True, False))
            
            # Add animation
            self.animations_data.append(animation_data)

    def play_animation(self, animation_name="", speed=1, animation_time=0, loop=False, on_animation_end = lambda self: 1, on_animation_interrupt = lambda self: 1):
        """ Start playing animation when rendering.

        Args:
            animation_name (str): Name of animation to be played.
            speed (float): Relative speed of animation which animation speed to be multiplied by.
            animation_time (float): Initial time in animation.
            loop (bool): Whether animation should be looped.
            on_animation_end (function): Function to be called when the animation completes.
            on_animation_interrupt (function): Function to be called if animation is interrupted by another, on_animation_end is not called.

        """
        # Call previous on_animation_interrupt and reassign
        self.on_animation_interrupt(self)
        self.on_animation_interrupt = on_animation_interrupt

        # Reset values
        self.animation_index = 0
        self.frame_num = 0
        self.speed = speed
        self.animation_finished = False
        self.animation_time = animation_time
        self.animation_looping = loop
        self.animation_playing = True
        self.on_animation_end = on_animation_end

        # Attempt to locate animation within data
        flag = True
        for i in range(len(self.animations_data)):
            if self.animations_data[i]["name"] == animation_name:
                self.animation_name = animation_name
                self.animation_index = i
                flag = False
        if flag and Settings.DEBUG:
            print(f"Animation {animation_name} not found")

    # https://stackoverflow.com/questions/57225611/how-to-deepcopy-object-which-contains-pygame-surface
    def copy(self):
        """ Standard copy constructor for complex objects """
        copyobj = AnimatedSprite()
        for name, attr in self.__dict__.items():
            if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
                copyobj.__dict__[name] = attr.copy()
            else:
                copyobj.__dict__[name] = copy.deepcopy(attr)
        return copyobj