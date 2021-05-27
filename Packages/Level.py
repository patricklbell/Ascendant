import pygame, json, copy, random, math
from Packages import Settings, Sprite, Enemy, Player, Water, Dialog

class Particle():
    """ Handles updating position and drawing a single particle 
    
    Args:
        position (pygame.Vector2): Initial position of particle (required).
        velocity (pygame.Vector2): Constant velocity experienced by particle (required).
        color (pygame.Color): Color particle is drawn with (required).
    """
    def __init__(self, position, velocity, color):
        self.position = position
        self.velocity = velocity
        self.color = color
    def update_position(self, delta):
        """ Update particle position.

        Args:
            delta (float): Time since last update.
        """
        # Apply velocity using dx = v * dt
        self.position += self.velocity * delta
    def render(self, surface, offset, delta=None):
        """ Draw particle to surface in Level space.
        Returns list of dirtys rects which have been drawn to.

        Args:
            surface (pygame.Surface): Surface to render to in level space.
            offset (pygame.Vector2): Camera position.
            delta (float): Time since last update.
        """
        if not delta == None:
            self.update_position(delta)
        rect = pygame.Rect(int(self.position.x+offset.x), int(self.position.y+offset.y), 2, 2) 
        surface.fill(self.color, rect)
        return [rect.inflate_ip(2, 2)]

class Level():
    """ General class for handling loading save and levels from disk and managing transitions .
    
    Args:
        should_load (bool): Flag if level name should be loaded immediately.
        level_name (int): Name of level to load first.
        position (pygame.Vector2): Offset between level rendering and world.
        player_base (Player.Player): Base object for Player which is copied into level.
        water_base (Water.Water): Base object for Water which is copied into level.
        enemy_base (Enemy.Enemy): Base object for Enemy which is copied into level.
        flying_enemy_base (Enemy.FlyingEnemy): Base object for FlyingEnemy which is copied into level.
        toxic_water_base (Water.Water): Base object for Water which is copied into level.
        collectable_base (Enemy.ChallengeCollectable): Base object for ChallengeCollectable which is copied into level.
    """
    def __init__(self, should_load=True, level_name="Tutorial1", position=pygame.Vector2(0,0), player_base=Player.Player(), water_base=Water.Water(), enemy_base=Enemy.Enemy(), flying_enemy_base=Enemy.FlyingEnemy(), toxic_water_base=Water.Water(), collectable_base=Enemy.ChallengeCollectable()):
        self.position = position
        self.player_base = player_base
        # Create initial player object
        self.player = player_base.copy()

        self.water_base = water_base
        self.toxic_water_base = toxic_water_base
        self.enemy_base = enemy_base
        self.flying_enemy_base = flying_enemy_base
        self.collectable_base = collectable_base

        # Setup rendering hierachy
        self.sprites_infront = []
        self.sprites_behind = []

        # Setup state
        self.level_name = level_name
        self.save_level = level_name

        # Setup collider arrays
        self.colliders, self.death_colliders, self.hitable_colliders, self.save_colliders, self.transitions, self.waters, self.water_colliders, self.toxic_waters, self.toxic_water_colliders,  self.enemies, self.collectables = [],[],[],[],[],[],[],[],[],[],[]

        self.dialog_boxes = []

        # Setup particles
        self.particles = []
        self.colors = [pygame.Color(0, 0, 0)]
        self.particles_likelihood = 0
        self.particles_min_velocity = [0,0]
        self.particles_max_velocity = [0,0]
        self.level_size = [0,0]

        # Setup filenames by substituting level name
        self.level_filename = f"{Settings.SRC_DIRECTORY}Levels/{self.level_name}/level.json"
        self.entities_filename = f"{Settings.SRC_DIRECTORY}Levels/{self.level_name}/entities.json"
        
        if should_load:
            self.load_level(level_name)
                
    def get_colliders(self):
        """ Getter for physical colliders"""
        return self.colliders

    def get_death_colliders(self):
        """ Getter for death colliders"""
        return self.death_colliders
    
    def get_hitable_colliders(self):
        """ Getter for hitable colliders"""
        return self.hitable_colliders
    
    def get_save_colliders(self):
        """ Getter for save colliders"""
        return self.save_colliders
    
    def get_water_colliders(self):
        """ Getter for water colliders"""
        return self.water_colliders + self.toxic_water_colliders

    def render_colliders(self, surface, offset):
        """ Draws level colliders to surface for debugging purposes.

        Args:
            surface (pygame.Surface): Surface to be rendered to (required).
            offset (pygame.Vector2): Camera position (required).
        """
        # Loop through each collider, offset by camera then draw in different color 
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
        # Extract colliders from transitions and dialog boxes
        for collider in [a["collider"] for a in self.transitions]:
            collider.move_ip(offset)
            pygame.draw.rect(surface, (100,0,200), collider)
            collider.move_ip(-offset)
        for collider in [a.collider for a in self.dialog_boxes]:
            collider.move_ip(offset)
            pygame.draw.rect(surface, (100,100,200), collider)
            collider.move_ip(-offset)

    def render_infront(self, delta, surface, offset=pygame.Vector2(0,0)):
        """ Render to surface parts of level which lie infront of entities and particles.
        Returns list of dirty rectangles which have been rendered to.

        Args:
            delta (float): Time since last rendering call, used to update particles (required).
            surface (pygame.Surface): Surface to be rendered to (required).
            offset (pygame.Vector2): Camera position.
        """
        dirty_rects = []

        # Handle generating new particles if their arent enough
        if random.uniform(0, 1) < self.particles_likelihood and len(self.particles) < self.particles_max:
            # Position randomly within level and give random velocity within level's range
            self.particles += [Particle(
                pygame.Vector2(random.randint(0, self.level_size[0]), random.randint(0, self.level_size[1])),
                pygame.Vector2(
                    random.uniform(self.particles_min_velocity[0], self.particles_max_velocity[0]),
                    random.uniform(self.particles_min_velocity[1], self.particles_max_velocity[1])
                ),
                random.choice(self.colors),
            )]
        # Loop through and draw each particle, delete particles which lie outside screen since they will never return
        i=0
        while i < len(self.particles):
            if self.particles[i].position.x < 0 or self.particles[i].position.x > self.level_size[0] or self.particles[i].position.y < 0 or self.particles[i].position.y > self.level_size[1]:
                del self.particles[i]
            else:
                dirty_rects += self.particles[i].render(surface, self.position + offset, delta)
                i+=1

        # Draw infront portion of water objects
        for sprite in self.waters + self.toxic_waters:
            dirty_rects += sprite.render_infront(delta, surface, self.position + offset)
        # Draw all infront sprites with added parallax effect
        for sprite in self.sprites_infront:
            render_position = self.position + pygame.Vector2(offset.x*sprite["parallax"].x, offset.y*sprite["parallax"].y)
            sprite["sprite"].render(surface, render_position)

        return dirty_rects

    def render_behind(self, delta, surface, offset=pygame.Vector2(0,0)):
        """ Render to surface parts of level which lie behind of entities.
        Returns list of dirty rectangles which have been rendered to.

        Args:
            delta (float): Time since last rendering call, used to update particles (required).
            surface (pygame.Surface): Surface to be rendered to (required).
            offset (pygame.Vector2): Camera position.

        """
        # Draw behind portion of waters
        for sprite in self.waters + self.toxic_waters:
            sprite.render_behind(delta, surface, self.position + offset)
        # Draw all behind sprites with added parallax effect
        for sprite in self.sprites_behind:
            render_position = self.position + pygame.Vector2(offset.x*sprite["parallax"].x, offset.y*sprite["parallax"].y)
            sprite["sprite"].render(surface, render_position)
    
    def load_save(self, save_num):
        """ Load save file from disk.

        Args:
            save_num (int): Number of save eg. 1, 2, 3
        """
        # Get filename and attempt to open save file for reaading
        self.selected_save = save_num
        save_filename = Settings.SAVE_FILETEMPLATE.substitute(num=str(save_num))
        try:
            with open(save_filename) as json_file:
                json_data = json.load(json_file)

            # Extract values into level object
            self.save_level = json_data["save_level"]
            self.dialog_completion = json_data["dialog_completion"]
            self.has_begun = json_data["has_begun"]
            self.name = json_data["name"]
            self.challenges = json_data["challenges"]

            # Load level which was saved at to respawn player
            self.load_level(level_name=json_data["save_level"])
        except Exception as e:
            if Settings.DEBUG:
                print(f"Failed to load save {save_filename}, error: ", e)
            
            # If loading the save failed write a new default save and load default values
            try:
                with open(save_filename, 'w') as file:
                    json.dump(Settings.DEFAULT_SAVE, file)
            except Exception as e:
                if Settings.DEBUG:
                    print(f"Failed to write save {save_filename}, error: ", e)
            self.save_level = copy.deepcopy(Settings.DEFAULT_SAVE["save_level"])
            self.dialog_completion = copy.deepcopy(Settings.DEFAULT_SAVE["dialog_completion"])
            self.has_begun = copy.deepcopy(Settings.DEFAULT_SAVE["has_begun"])
            self.name = copy.deepcopy(Settings.DEFAULT_SAVE["name"])
            self.challenges = copy.deepcopy(Settings.DEFAULT_SAVE["challenges"])
            self.load_level(self.save_level)
        # Update save dialog completetion to intially match loaded
        self.save_dialog_completion = copy.deepcopy(self.dialog_completion)
        # Play unsit and add lives for collectables
        self.player.play_animation("unsit")
        self.player.hearts += len(self.collectables)
    def save_game(self):
        """ Writes current level properties to the currently selected save file """
        # Get filename
        save_filename = Settings.SAVE_FILETEMPLATE.substitute(num=str(Settings.SELECTED_SAVE))

        # Construct save data object by copying default and changing values
        save_data = copy.deepcopy(Settings.DEFAULT_SAVE)
        save_data["name"] = self.name
        # Signal save has begun if they saved anywhere
        save_data["has_begun"] = self.has_begun or not (self.save_level == Settings.DEFAULT_SAVE["save_level"])
        save_data["save_level"] = self.save_level
        save_data["dialog_completion"] = self.save_dialog_completion
        save_data["challenges"] = self.challenges

        percent_completion = math.floor((len(self.save_dialog_completion) / 14)*1000)/10
        save_data["title_info"]["percentage_completion"] = percent_completion

        # Update gui labels and buttons to reflect new save data
        if save_data["has_begun"]:
            Settings.gui.menus["select_save"][f"save{Settings.SELECTED_SAVE}_label"].set_text(f"SAVE {Settings.SELECTED_SAVE} ({percent_completion}%): {self.name[:6] + (self.name[6:] and '..')}")
            Settings.gui.menus["select_save"][f"save{Settings.SELECTED_SAVE}"].set_text("CONTINUE")
        else:
            Settings.gui.menus["select_save"][f"save{Settings.SELECTED_SAVE}_label"].set_text(f"SAVE {Settings.SELECTED_SAVE}")
            Settings.gui.menus["select_save"][f"save{Settings.SELECTED_SAVE}"].set_text("NEW GAME")
        Settings.gui.has_begun[Settings.SELECTED_SAVE-1] = save_data["has_begun"]

        # Attempt to actually write to file
        try:
            with open(save_filename, 'w') as file:
                json.dump(save_data, file)
        except Exception as e:
            if Settings.DEBUG:
                print(f"Failed to write save {save_filename}, error: ", e)

    def load_level(self, level_name="Tutorial1", transition=None):
        """ Load level from level directory and handle transitions

        Args:
            level_name (str): Name of directory of level (required).
            transition (dict): Optional transition that player is entering level from.
        """
        # Get filename and read level json data
        self.level_name=level_name
        self.level_filename = f"{Settings.SRC_DIRECTORY}Levels/{self.level_name}/level.json"
        with open(self.level_filename) as json_file:
            level_json_data = json.load(json_file)
        
        # Sort layers of level by depth
        sorted_layers = sorted(level_json_data["layers"], key = lambda x: x["depth"])
        # Reset sprite lists and place anything of depth <= 0 behind entities
        self.sprites_behind, self.sprites_infront = [],[]
        for image_layer in sorted_layers:
            if image_layer["depth"] <= 0:
                # Construct image sprite from filenames and save parallax and depth
                self.sprites_behind.append({
                    "sprite": Sprite.ImageSprite( image_filename=f"{Settings.SRC_DIRECTORY}Levels/{self.level_name}/{image_layer['filename']}"),
                    "depth": image_layer["depth"],
                    "parallax": pygame.Vector2(image_layer["parallaxX"],image_layer["parallaxY"])   
                })
            else:
                self.sprites_infront.append({
                    "sprite": Sprite.ImageSprite( image_filename=f"{Settings.SRC_DIRECTORY}Levels/{self.level_name}/{image_layer['filename']}"),
                    "depth": image_layer["depth"],
                    "parallax": pygame.Vector2(image_layer["parallaxX"],image_layer["parallaxY"])   
                })
        # Determine level size from first behind level sprite
        # NOTE: Fails when no behind layer exists
        self.level_size = [self.sprites_behind[0]["sprite"].image.get_width(), self.sprites_behind[0]["sprite"].image.get_height()]

        # Intialize particles randomly across screen with correct colours and velocity ranges
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
            for _ in range(self.particles_max):
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

        # Load entities json data describing rectangular shaps for colliders and position of entities
        self.entities_filename = f"{Settings.SRC_DIRECTORY}Levels/{self.level_name}/{level_json_data['entities']['filename']}"
        with open(self.entities_filename) as json_file:
            json_data = json.load(json_file)

        # Load each entity from json data
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
        
        # Attempt to load transitions
        self.transitions = []   
        try:
            # Transition dictionaries require data from both level and entity file so zip together lists to traverse together
            for bounds, info in zip(json_data["level_transition"], level_json_data["level_transition"]):
                self.transitions.append({
                    "collider":pygame.Rect(bounds["x"], bounds["y"], bounds["width"], bounds["height"]),
                    "to_level":info["to_level"],
                    "to_transition":info["to_transition"],
                    "direction":info["direction"]
                })
        except:
            if Settings.DEBUG:
                print(f"Failed to load transition entities {self.entities_filename}, and/or {self.level_filename}")

        # Load water entities by calling tile from rect on size collider
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

        # Again traverse data together to extract constant and boundary info
        self.dialog_boxes = []
        if "dialog" in json_data and "dialog" in level_json_data:
            for bounds, info in zip(json_data["dialog"], level_json_data["dialog"]):
                if (not info["save_progress_name"] in self.dialog_completion) or (not self.dialog_completion[info["save_progress_name"]]):
                    self.dialog_boxes.append(Dialog.Dialog(
                        info["text"],
                        pygame.Rect(bounds["x"], bounds["y"], bounds["width"], bounds["height"]),
                        info["save_progress_name"]
                    ))
        elif Settings.DEBUG:
            print(f"No dialog entity layer found in {self.entities_filename} and/or {self.level_filename}")
            
        # Load resetable elements of level eg. player and enemies
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

            # Handle each direction by positioning appropriately and giving sufficient initial velocity to not fall back
            if direction == "S":
                self.player.velocity.y = -self.player.gravity.y/9.6
                self.player.velocity.x = self.player.gravity.y/25
                self.player.position = pygame.Vector2(
                    transition_rect.left + transition_rect.width - 3*self.player.collider_size.x,
                    transition_rect.top,
                ) - self.player.collider_offset
            elif direction == "N":
                self.player.velocity.y = self.player.gravity.y/4
                self.player.position = pygame.Vector2(
                    transition_rect.left + transition_rect.width*0.5,
                    transition_rect.top,
                ) - self.player.collider_offset
            elif direction == "W":
                self.player.velocity.x = self.player.walk_speed
                self.player.position = pygame.Vector2(
                    transition_rect.left - transition_rect.width + self.player.collider_size.y/2,
                    transition_rect.top + transition_rect.height - self.player.collider_size.y,
                ) - self.player.collider_offset
                self.player.play_animation("walk", loop=True)
            elif direction == "E":
                self.player.velocity.x = -self.player.walk_speed
                self.player.position = pygame.Vector2(
                    transition_rect.left + transition_rect.width - self.player.collider_size.y/2,
                    transition_rect.top + transition_rect.height - self.player.collider_size.y,
                ) - self.player.collider_offset
                self.player.play_animation("walk", loop=True)
                self.player.flipX = True
        # Jump camera to correct position
        Settings.camera.set_position(self.player.position, Settings.surface)
    def reset_level(self):
        """ Load parts of level which are reset when player dies """
        # Load entities data
        with open(self.entities_filename) as json_file:
            json_data = json.load(json_file)

        # Load player while maintaining number of hearts and key state
        if "player" in json_data:
            old_player_hearts = self.player.hearts
            old_player_key_state = self.player.key_state

            player_info = json_data["player"][0]
            self.player = self.player_base.copy()
            # Extract position from entities
            self.player.position = pygame.Vector2(
                player_info["x"] - self.player.collider_offset.x,
                player_info["y"] - self.player.collider_offset.x,
            )
            self.player.hearts = old_player_hearts
            self.player.key_state = old_player_key_state
        elif Settings.DEBUG:
            print(f"No players entity layer found in {self.entities_filename}")

        # Load patrolling and flying enemies and position correctly
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
        
        # Load collectable if player hasnt already collected them
        if self.level_name not in self.challenges:
            self.collectables = []
            if "collectables" in json_data:
                for collectable in json_data["collectables"]:
                    self.collectables.append(self.collectable_base.copy())
                    self.collectables[-1].position = pygame.Vector2(
                        collectable["x"] - self.collectable_base.collider_offset.x,
                        collectable["y"] - self.collectable_base.collider_offset.y,
                    )
                    self.collectables[-1].og_position = copy.copy(self.collectables[-1].position)
            elif Settings.DEBUG:
                print(f"No collectables entity layer found in {self.entities_filename}")