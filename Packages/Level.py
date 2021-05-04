import pygame, json, copy, random, math
from pygame.rect import Rect

from pygame.version import PygameVersion

from Packages.Extern import SoundPlayer
from Packages import Settings, Sprite, Enemy, Player, Water, Dialog

class Particle():
    """ """
    def __init__(self, position, velocity, color):
        self.position = position
        self.velocity = velocity
        self.color = color
    def update_position(self, delta):
        """

        :param delta: 

        """
        self.position += self.velocity * delta
    def render(self, surface, offset, delta=None):
        """

        :param surface: 
        :param offset: 
        :param delta:  (Default value = None)

        """
        if not delta == None:
            self.update_position(delta)
        rect = pygame.Rect(int(self.position.x+offset.x), int(self.position.y+offset.y), 2, 2) 
        surface.fill(self.color, rect)
        return [rect.inflate_ip(2, 2)]

class Level():
    """ """
    def __init__(self, should_load=True, level_num=0, save_num=0, position=pygame.Vector2(0,0), player_base=Player.Player(), water_base=Water.Water(), enemy_base=Enemy.Enemy(), flying_enemy_base=Enemy.FlyingEnemy(), toxic_water_base=Water.Water()):
        self.position = position

        self.sprites_infront = []
        self.sprites_behind = []
        self.level_num = level_num
        self.save_level = 0

        self.player_base = player_base
        self.water_base = water_base
        self.toxic_water_base = toxic_water_base
        self.enemy_base = enemy_base
        self.flying_enemy_base = flying_enemy_base

        self.colliders, self.death_colliders, self.hitable_colliders, self.save_colliders, self.transitions, self.waters, self.water_colliders, self.toxic_waters, self.toxic_water_colliders,  self.enemies = [],[],[],[],[],[],[],[],[],[]
        self.dialog_boxes = []
        self.player = player_base.copy()
        self.particles = []
        self.colors = [pygame.Color(0, 0, 0)]
        self.particles_likelihood = 0
        self.particles_min_velocity = [0,0]
        self.particles_max_velocity = [0,0]
        self.level_size = [0,0]


        self.level_filename = f"{Settings.SRC_DIRECTORY}Levels/Level{self.level_num}/level.json"
        self.entities_filename = f"{Settings.SRC_DIRECTORY}Levels/Level{self.level_num}/entities.json"
        
        if should_load:
            self.load_level(level_num)
                
    def get_colliders(self):
        """ """
        return self.colliders

    def get_death_colliders(self):
        """ """
        return self.death_colliders
    
    def get_hitable_colliders(self):
        """ """
        return self.hitable_colliders
    
    def get_save_colliders(self):
        """ """
        return self.save_colliders
    
    def get_water_colliders(self):
        """ """
        return self.water_colliders + self.toxic_water_colliders

    def render_colliders(self, delta, surface, offset):
        """

        :param delta: 
        :param surface: 
        :param offset: 

        """
        for collider in self.colliders:
            collider.move_ip(offset)
            pygame.draw.rect(surface, (255,0,0), collider)
            collider.move_ip(-offset)
        for collider in self.hitable_colliders:
            collider.move_ip(offset)
            pygame.draw.rect(surface, (100,0,100), collider)
            collider.move_ip(-offset)
        for collider in self.death_colliders:
            collider.move_ip(offset)
            pygame.draw.rect(surface, (200,0,100), collider)
            collider.move_ip(-offset)
        for collider in self.water_colliders:
            collider.move_ip(offset)
            pygame.draw.rect(surface, (100,150,200), collider)
            collider.move_ip(-offset)
        for collider in self.toxic_water_colliders:
            collider.move_ip(offset)
            pygame.draw.rect(surface, (200,150,100), collider)
            collider.move_ip(-offset)
        for collider in [a["collider"] for a in self.transitions]:
            collider.move_ip(offset)
            pygame.draw.rect(surface, (100,0,200), collider)
            collider.move_ip(-offset)
        for collider in [a.collider for a in self.dialog_boxes]:
            collider.move_ip(offset)
            pygame.draw.rect(surface, (100,100,200), collider)
            collider.move_ip(-offset)

    def render_infront(self, delta, surface, offset=pygame.Vector2(0,0)):
        """

        :param delta: 
        :param surface: 
        :param offset:  (Default value = pygame.Vector2(0)
        :param 0): 

        """
        dirty_rects = []

        # Handle particles
        if random.uniform(0, 1) < self.particles_likelihood and len(self.particles) < self.particles_max:
            self.particles += [Particle(
                pygame.Vector2(0, random.randint(0, self.level_size[1])),
                pygame.Vector2(
                    random.uniform(self.particles_min_velocity[0], self.particles_max_velocity[0]),
                    random.uniform(self.particles_min_velocity[1], self.particles_max_velocity[1])
                ),
                random.choice(self.colors),
            )]
        i=0
        while i < len(self.particles):
            if self.particles[i].position.x < 0 or self.particles[i].position.x > self.level_size[0] or self.particles[i].position.y < 0 or self.particles[i].position.y > self.level_size[1]:
                del self.particles[i]
            else:
                dirty_rects += self.particles[i].render(surface, self.position + offset, delta)
                i+=1

        for sprite in self.waters + self.toxic_waters:
            dirty_rects += sprite.render_infront(delta, surface, self.position + offset)
        for sprite in self.sprites_infront:
            render_position = self.position + pygame.Vector2(offset.x*sprite["parallax"].x, offset.y*sprite["parallax"].y)
            sprite["sprite"].render(surface, render_position)
        
        for dialogue_box in self.dialog_boxes:
            dialogue_box.render(surface)

        return dirty_rects

    def render_behind(self, delta, surface, offset=pygame.Vector2(0,0)):
        """

        :param delta: 
        :param surface: 
        :param offset:  (Default value = pygame.Vector2(0)
        :param 0): 

        """
        for sprite in self.waters + self.toxic_waters:
            sprite.render_behind(delta, surface, self.position + offset)
        for sprite in self.sprites_behind:
            render_position = self.position + pygame.Vector2(offset.x*sprite["parallax"].x, offset.y*sprite["parallax"].y)
            sprite["sprite"].render(surface, render_position)
    
    def load_save(self, save_num):
        """

        :param save_num: 

        """
        self.selected_save = save_num
        save_filename = Settings.SAVE_FILETEMPLATE.substitute(num=str(save_num))
        try:
            with open(save_filename) as json_file:
                json_data = json.load(json_file)
            self.load_level(level_num=json_data["save_level"])
            self.save_level = json_data["save_level"]
            self.dialog_completion = json_data["dialog_completion"]
        except Exception as e:
            if Settings.DEBUG:
                print(f"Failed to load save {save_filename}, error: ", e)
            try:
                with open(save_filename, 'w') as file:
                    json.dump(Settings.DEFAULT_SAVE, file)
            except Exception as e:
                if Settings.DEBUG:
                    print(f"Failed to write save {save_filename}, error: ", e)
            self.load_level()
            self.save_level = Settings.DEFAULT_SAVE["save_level"]
            self.dialog_completion = Settings.DEFAULT_SAVE["dialog_completion"]
        self.save_dialog_completion = copy.deepcopy(self.dialog_completion)
        self.player.play_animation("unsit")
        
    def save_game(self):
        """ """
        save_filename = Settings.SAVE_FILETEMPLATE.substitute(num=str(Settings.SELECTED_SAVE))
        save_data = Settings.DEFAULT_SAVE
        save_data["save_level"] = self.save_level
        save_data["dialog_completion"] = self.save_dialog_completion

        percent_completion = math.floor((len(self.save_dialog_completion) / 24)*1000)/10
        save_data["title_info"]["percentage_completion"] = percent_completion

        # Update percentage completion in gui
        Settings.gui.select_save_gui[f"save{Settings.SELECTED_SAVE}_label"].set_text(f"SAVE 1 ({percent_completion}%):")
        Settings.gui.completions[Settings.SELECTED_SAVE-1] = percent_completion

        try:
            with open(save_filename, 'w') as file:
                json.dump(Settings.DEFAULT_SAVE, file)
        except Exception as e:
            if Settings.DEBUG:
                print(f"Failed to write save {save_filename}, error: ", e)

    def load_level(self, level_num=0, transition=None):
        """

        :param level_num:  (Default value = 0)
        :param transition:  (Default value = None)

        """
        self.level_num=level_num
        self.level_filename = f"{Settings.SRC_DIRECTORY}Levels/Level{self.level_num}/level.json"

        with open(self.level_filename) as json_file:
            level_json_data = json.load(json_file)
        
        sorted_layers = sorted(level_json_data["layers"], key = lambda x: x["depth"])
        self.sprites_behind, self.sprites_infront = [],[]
        for image_layer in sorted_layers:
            if image_layer["depth"] <= 0:
                self.sprites_behind.append({
                    "sprite": Sprite.ImageSprite( image_filename=f"{Settings.SRC_DIRECTORY}Levels/Level{self.level_num}/{image_layer['filename']}"),
                    "depth": image_layer["depth"],
                    "parallax": pygame.Vector2(image_layer["parallaxX"],image_layer["parallaxY"])   
                })
            else:
                self.sprites_infront.append({
                    "sprite": Sprite.ImageSprite( image_filename=f"{Settings.SRC_DIRECTORY}Levels/Level{self.level_num}/{image_layer['filename']}"),
                    "depth": image_layer["depth"],
                    "parallax": pygame.Vector2(image_layer["parallaxX"],image_layer["parallaxY"])   
                })
        self.level_size = [self.sprites_behind[0]["sprite"].image.get_width(), self.sprites_behind[0]["sprite"].image.get_height()]

        if "particles" in level_json_data:
            self.particles_max_velocity = level_json_data["particles"]["max_velocity"]
            self.particles_min_velocity = level_json_data["particles"]["min_velocity"]
            self.particles_likelihood   = level_json_data["particles"]["likelihood"]
            self.particles_max          = level_json_data["particles"]["max"]
            self.colors = []
            for color in level_json_data["particles"]["colors"]:
                self.colors.append(pygame.Color(*color))
            
            # Randomize intial particles
            self.particles = []
            for i in range(self.particles_max):
                self.particles += [Particle(
                    pygame.Vector2(random.randint(0, self.level_size[0]), random.randint(0, self.level_size[1])),
                    pygame.Vector2(
                        random.uniform(self.particles_min_velocity[0], self.particles_max_velocity[0]),
                        random.uniform(self.particles_min_velocity[1], self.particles_max_velocity[1])
                    ),
                    random.choice(self.colors),
                )]
        elif Settings.DEBUG:
            print("No particles data found in", self.level_filename)

        self.entities_filename = f"{Settings.SRC_DIRECTORY}Levels/Level{self.level_num}/{level_json_data['entities']['filename']}"
        with open(self.entities_filename) as json_file:
            json_data = json.load(json_file)

        self.colliders = []
        if "collisions" in json_data:
            for collider in json_data["collisions"]:
                self.colliders.append(pygame.Rect(collider["x"], collider["y"], collider["width"], collider["height"]))
        elif Settings.DEBUG:
            print(f"No collisions entity layer found in {self.entities_filename}")
        
        self.death_colliders = []
        if "death_colliders" in json_data:
            for collider in json_data["death_colliders"]:
                self.death_colliders.append(pygame.Rect(collider["x"], collider["y"], collider["width"], collider["height"]))
        elif Settings.DEBUG:
            print(f"No death_colliders entity layer found in {self.entities_filename}")

        self.hitable_colliders = []
        if "hitable_colliders" in json_data:
            for collider in json_data["hitable_colliders"]:
                self.hitable_colliders.append(pygame.Rect(collider["x"], collider["y"], collider["width"], collider["height"]))
        elif Settings.DEBUG:
            print(f"No hitable_colliders entity layer found in {self.entities_filename}")

        self.save_colliders = []
        if "save_game" in json_data:
            for collider in json_data["save_game"]:
                self.save_colliders.append(pygame.Rect(collider["x"], collider["y"], collider["width"], collider["height"]))
        elif Settings.DEBUG:
            print(f"No save_games entity layer found in {self.entities_filename}")
        
        self.transitions = []
        try:
            for bounds, info in zip(json_data["level_transition"], level_json_data["level_transition"]):
                self.transitions.append({
                    "collider":pygame.Rect(bounds["x"], bounds["y"], bounds["width"], bounds["height"]),
                    "to_level":info["to_level"],
                    "to_transition":info["to_transition"],
                    "direction":["N", "E", "S", "W"][info["direction"]]
                })
        except:
            if Settings.DEBUG:
                print(f"Failed to load transition entities {self.entities_filename}, and {self.level_filename}")

        self.waters = []
        self.water_colliders = []
        if "water" in json_data:
            for water in json_data["water"]:
                self.waters.append(self.water_base.copy())
                self.waters[-1].tile_from_rect(pygame.Rect(water["x"], water["y"], water["width"], water["height"]))
                self.water_colliders.append(pygame.Rect(water["x"], water["y"], water["width"], water["height"]))
        elif Settings.DEBUG:
            print(f"No water entity layer found in {self.entities_filename}")
        
        self.toxic_waters = []
        self.toxic_water_colliders = []
        if "toxic_water" in json_data:
            for toxic_water in json_data["toxic_water"]:
                self.toxic_waters.append(self.toxic_water_base.copy())
                self.toxic_waters[-1].tile_from_rect(pygame.Rect(toxic_water["x"], toxic_water["y"], toxic_water["width"], toxic_water["height"]))
                self.toxic_water_colliders.append(pygame.Rect(toxic_water["x"], toxic_water["y"], toxic_water["width"], toxic_water["height"]))
        elif Settings.DEBUG:
            print(f"No toxic_water entity layer found in {self.entities_filename}")

        self.dialog_boxes = []
        if "dialog" in json_data and "dialog" in level_json_data:
            for bounds, info in zip(json_data["dialog"], level_json_data["dialog"]):
                if (not info["save_progress_name"] in self.dialog_completion) or (not self.dialog_completion[info["save_progress_name"]]):
                    self.dialog_boxes.append(Dialog.Dialog(
                        info["text"],
                        pygame.Rect(bounds["x"], bounds["y"], bounds["width"], bounds["height"]),
                        info["save_progress_name"],
                    ))
        elif Settings.DEBUG:
            print(f"No dialog entity layer found in {self.entities_filename} and/or {self.level_filename}")

        self.reset_level()

        # Configure level settings
        Settings.camera.contraints_max = pygame.Vector2(
            self.sprites_behind[0]["sprite"].image.get_rect().width,
            self.sprites_behind[0]["sprite"].image.get_rect().height,
        )

        # Handle transition
        if not transition == None:
            transition_rect = self.transitions[transition["to_transition"]]["collider"]
            direction = self.transitions[transition["to_transition"]]["direction"]

            self.player.transition_frames = self.player.transition_max_frames

            if direction == "N":
                self.player.velocity.y = -self.player.gravity.y/4
                self.player.position = pygame.Vector2(
                    transition_rect.left + transition_rect.width*0.5 - self.player.collider_size.x*0.5,
                    transition_rect.top,
                ) - self.player.collider_offset
            elif direction == "S":
                self.player.velocity.y = self.player.gravity.y/4
                self.player.position = pygame.Vector2(
                    transition_rect.left + transition_rect.width*0.5,
                    transition_rect.top,
                ) - self.player.collider_offset
            elif direction == "E":
                self.player.transition_frames = self.player.transition_max_frames
                self.player.velocity.x = self.player.walk_speed
                self.player.position = pygame.Vector2(
                    transition_rect.left + transition_rect.width,
                    transition_rect.top + transition_rect.height*0.5,
                ) - self.player.collider_offset
                self.player.play_animation("walk", loop=True)
            elif direction == "W":
                self.player.transition_frames = self.player.transition_max_frames
                self.player.velocity.x = -self.player.walk_speed
                self.player.position = pygame.Vector2(
                    transition_rect.left,
                    transition_rect.top + transition_rect.height - self.player.collider_size.y,
                ) - self.player.collider_offset
                self.player.play_animation("walk", loop=True)
                self.player.flipX = True

        Settings.camera.set_position(self.player.position, Settings.surface)
    
    def reset_level(self):
        """ """
        with open(self.entities_filename) as json_file:
            json_data = json.load(json_file)

        if "player" in json_data:
            old_player_hearts = self.player.hearts
            old_player_key_state = self.player.key_state

            player_info = json_data["player"][0]
            self.player = self.player_base.copy()
            self.player.position = pygame.Vector2(
                player_info["x"] - self.player.collider_offset.x,
                player_info["y"] - self.player.collider_offset.x,
            )
            self.player.hearts = old_player_hearts
            self.player.key_state = old_player_key_state
        elif Settings.DEBUG:
            print(f"No players entity layer found in {self.entities_filename}")

        self.enemies = []
        if "enemies" in json_data:
            for enemy in json_data["enemies"]:
                self.enemies.append(self.enemy_base.copy())
                self.enemies[-1].position = pygame.Vector2(
                    enemy["x"] - self.enemy_base.collider_offset.x,
                    enemy["y"] - self.enemy_base.collider_offset.y,
                )
        elif Settings.DEBUG:
            print(f"No enemies entity layer found in {self.entities_filename}")

        if "flying_enemies" in json_data:
            for enemy in json_data["flying_enemies"]:
                self.enemies.append(self.flying_enemy_base.copy())
                self.enemies[-1].position = pygame.Vector2(
                    enemy["x"] - self.flying_enemy_base.collider_offset.x,
                    enemy["y"] - self.flying_enemy_base.collider_offset.y,
                )
                self.enemies[-1].og_position = copy.copy(self.enemies[-1].position)
        elif Settings.DEBUG:
            print(f"No flying_enemies entity layer found in {self.entities_filename}")