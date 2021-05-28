import pygame, json, copy, random


# For debugging
from Packages import Sprite

class Water():
    """ Creates water with randomly distributed bubbles and grass from a rect.
    
    Args:
        spritesheet_scale (tuple): x, y componenets to scale spritesheet by.
        water_rect (pygame.Rect): Rectangle to tile with water sprites.
        waterbase_json_filename (str): Path of image sprite json file containing background and grass.
        water_json_filename (str): Path of animation sprite json file for slightly bubbly water.
        water_bubbly_json_filename (str): Path of animation sprite json file for bubbly water.
        water_bubbliest_json_filename (str): Path of animation sprite json file for very bubbly water.
    """
    def __init__(self, spritesheet_scale=(1,1), water_rect=None, waterbase_json_filename=None, water_json_filename=None, water_bubbly_json_filename=None, water_bubbliest_json_filename=None):
        # Load each json file as image sprites and animated sprites
        if not waterbase_json_filename == None:
            self.waterbase = Sprite.ImageSpriteSheet(spritesheet_json_filename=waterbase_json_filename, spritesheet_scale=spritesheet_scale)
            # Get width to tile later
            self.width = self.waterbase.images["base"].get_rect().width
        if not water_json_filename == None:
            self.water = Sprite.AnimatedSprite(spritesheet_json_filename=water_json_filename, spritesheet_scale=spritesheet_scale)
        if not water_bubbly_json_filename == None:
            self.water_bubbly = Sprite.AnimatedSprite(spritesheet_json_filename=water_bubbly_json_filename, spritesheet_scale=spritesheet_scale)
        if not water_bubbliest_json_filename == None:
            self.water_bubbliest = Sprite.AnimatedSprite(spritesheet_json_filename=water_bubbliest_json_filename, spritesheet_scale=spritesheet_scale)

        # Setup rendering buffers and actually tile water rect
        self.image_infront = None
        self.image_behind = None
        self.animated_sprite_tiles = []
        if not water_rect == None:
            self.tile_from_rect(water_rect)
    
    def tile_from_rect(self, rect, grass_density=3/4, bubble_density=1/6, bubbly_density=1/8, bubbliest_density=1/16):
        """

            rect (pygame.Rect): 
            grass_density (float): Fraction of tiles which are grassy.
            bubble_density (float): Fraction of tiles which are slightly bubbly.
            bubbly_density (float): Fraction of tiles which are bubbly.
            bubbliest_density (float): Fraction of tiles which are very bubbly.

        """
        # Add row so their is no gap at end
        rows = int(rect.width / self.width +1)

        # Create static images of correct size, adding pixel for edge
        self.image_infront = pygame.Surface(rect.size+pygame.Vector2(1,1), pygame.SRCALPHA).convert_alpha()
        self.image_behind =  pygame.Surface(rect.size+pygame.Vector2(1,1)).convert()
        self.image_infront.set_colorkey((0,0,0))

        self.position = pygame.Vector2(rect.left, rect.top)

        # Render static images to behind and infront images
        for i in range(rows):
            offset = pygame.Vector2(i*self.width, 0)

            self.waterbase.render(self.image_infront, "base", offset)

            # Add grass randomly infront of base
            if random.uniform(0,1) <= grass_density:
                self.waterbase.render(self.image_infront, "grass", offset)

            # Render foam behind player
            self.waterbase.render(self.image_behind, "foam", offset)

            # Append animated sprites to list
            if random.uniform(0,1) <= bubbliest_density:
                new_tile = self.water_bubbliest.copy()
                # Set position correctly
                new_tile.position = self.position + offset
                new_tile.play_animation("loop", loop=True)

                # Offset animation times of tiles
                new_tile.animation_time = random.uniform(0, new_tile.animations_data[new_tile.animation_index]["time"])

                self.animated_sprite_tiles.append(new_tile)
            elif random.uniform(0,1) <= bubbly_density:
                new_tile = self.water_bubbly.copy()
                new_tile.position = self.position + offset
                new_tile.play_animation("loop", loop=True)
                new_tile.animation_time = random.uniform(0, new_tile.animations_data[new_tile.animation_index]["time"])
                self.animated_sprite_tiles.append(new_tile)
            elif random.uniform(0,1) <= bubble_density:
                new_tile = self.water.copy()
                new_tile.position = self.position + offset
                new_tile.play_animation("loop", loop=True)
                new_tile.animation_time = random.uniform(0, new_tile.animations_data[new_tile.animation_index]["time"])
                self.animated_sprite_tiles.append(new_tile)
        # Apply transparency to infront images
        self.image_infront.convert_alpha()
    def render_infront(self, delta, surface, offset=pygame.Vector2(0,0)):
        """ Draw parts of water which lie infront of entities
        Returns list of dirty rects which have been rendered to.

        Args:
            delta (float): Seconds since last render infront call, used to update animations (required). 
            surface (pygame.Surface): Surface to render to (required).
            offset (pygame.Vector2): Offset between position of water and render position.
        """
        # Draw static images
        surface.blit(self.image_infront, self.position + offset)

        # Draw and update each of the animated tiles
        for tile in self.animated_sprite_tiles:
            tile.render(surface, offset, delta=delta)

        # Since all relevant animations lie within static image, just return its rect
        return [self.image_infront.get_rect()]
    def render_behind(self, delta, surface, offset=pygame.Vector2(0,0)):
        """ Draw parts of water which lie behind of entities
        Returns list of dirty rects which have been rendered to.

        Args:
            delta (float): Unused argument for consistency, eg. 0. 
            surface (pygame.Surface): Surface to render to (required).
            offset (pygame.Vector2): Offset between position of water and render position.
        """
        return [surface.blit(self.image_behind, self.position + offset)]
    
    # https://stackoverflow.com/questions/57225611/how-to-deepcopy-object-which-contains-pygame-surface
    def copy(self):
        """ Standard copy constructor for complex objects """
        copyobj = Water()
        for name, attr in self.__dict__.items():
            if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
                copyobj.__dict__[name] = attr.copy()
            else:
                copyobj.__dict__[name] = copy.deepcopy(attr)

        return copyobj