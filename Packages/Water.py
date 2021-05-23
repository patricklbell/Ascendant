import pygame, json, copy, random


# For debugging
from Packages import Settings, Sprite

class Water():
    """ """
    def __init__(self, position=(0,0), spritesheet_scale=(1,1), water_rect=None, waterbase_json_filename=None, water_json_filename=None, water_bubbly_json_filename=None, water_bubbliest_json_filename=None):
        if not waterbase_json_filename == None:
            self.waterbase = Sprite.ImageSpriteSheet(spritesheet_json_filename=waterbase_json_filename, spritesheet_scale=spritesheet_scale)
            self.width = self.waterbase.images["base"].get_rect().width
        if not water_json_filename == None:
            self.water = Sprite.AnimatedSprite(spritesheet_json_filename=water_json_filename, spritesheet_scale=spritesheet_scale)
        if not water_bubbly_json_filename == None:
            self.water_bubbly = Sprite.AnimatedSprite(spritesheet_json_filename=water_bubbly_json_filename, spritesheet_scale=spritesheet_scale)
        if not water_bubbliest_json_filename == None:
            self.water_bubbliest = Sprite.AnimatedSprite(spritesheet_json_filename=water_bubbliest_json_filename, spritesheet_scale=spritesheet_scale)

        self.image_infront = None
        self.image_behind = None
        self.animated_sprite_tiles = []
        if not water_rect == None:
            self.tile_from_rect(water_rect)
    
    def tile_from_rect(self, rect, grass_density=3/4, bubble_density=1/6, bubbly_density=1/8, bubbliest_density=1/16):
        """

        :param rect: 
        :param grass_density:  (Default value = 3/4)
        :param bubble_density:  (Default value = 1/2)
        :param bubbly_density:  (Default value = 1/4)
        :param bubbliest_density:  (Default value = 1/6)

        """
        rows = int(rect.width / self.width +1)
        self.image_infront = pygame.Surface(rect.size+pygame.Vector2(1,1), pygame.SRCALPHA).convert_alpha()
        self.image_behind =  pygame.Surface(rect.size+pygame.Vector2(1,1)).convert()
        self.image_infront.set_colorkey((0,0,0))
        self.position = pygame.Vector2(rect.left, rect.top)

        for i in range(rows):
            offset = pygame.Vector2(i*self.width, 0)
            self.waterbase.render(self.image_infront, "base", offset)

            if random.uniform(0,1) <= grass_density:
                self.waterbase.render(self.image_infront, "grass", offset)

            self.waterbase.render(self.image_behind, "foam", offset)

            if random.uniform(0,1) <= bubbliest_density:
                new_tile = self.water_bubbliest.copy()
                new_tile.position = self.position + offset
                new_tile.play_animation("loop", loop=True)
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
        self.image_infront.convert_alpha()
    def render_infront(self, delta, surface, offset=pygame.Vector2(0,0)):
        """

        :param delta: 
        :param surface: 
        :param offset:  (Default value = pygame.Vector2(0)
        :param 0): 

        """
        surface.blit(self.image_infront, self.position + offset)
        for tile in self.animated_sprite_tiles:
            tile.render(surface, offset, delta=delta)
        return [self.image_infront.get_rect()]
    def render_behind(self, delta, surface, offset=pygame.Vector2(0,0)):
        """

        :param delta: 
        :param surface: 
        :param offset:  (Default value = pygame.Vector2(0)
        :param 0): 

        """
        surface.blit(self.image_behind, self.position + offset)
        return []
    
    # https://stackoverflow.com/questions/57225611/how-to-deepcopy-object-which-contains-pygame-surface
    def copy(self):
        """ """
        copyobj = Water()
        for name, attr in self.__dict__.items():
            if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
                copyobj.__dict__[name] = attr.copy()
            else:
                copyobj.__dict__[name] = copy.deepcopy(attr)

        return copyobj
