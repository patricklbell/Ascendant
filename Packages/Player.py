import pygame, json, itertools, pygame_gui, copy, random

from Packages.Extern import SoundPlayer
from Packages import Settings, Sprite

class Player(Sprite.AnimatedSprite):
    """ """
    def __init__(self, *args, **kwargs):
        Sprite.AnimatedSprite.__init__(self, *args, **kwargs)

        # Setup physics
        self.gravity = kwargs.get("gravity", pygame.Vector2(0,500))
        self.air_resistance = kwargs.get("air_resistance", 1)
        self.floor_resistance = kwargs.get("floor_resistance", 10)
        self.water_resistance = kwargs.get("water_resistance", 9)
        self.walk_speed = kwargs.get("walk_speed", 200)
        self.water_walk_speed = kwargs.get("water_walk_speed", 100)
        self.jump_speed = kwargs.get("jump_speed", -200)
        self.jump_add_speed = kwargs.get("jump_add_speed", -500)
        self.jump_add_max_time = kwargs.get("jump_add_max_time", 1)
        self.jump_add_time = 0
        self.jumping = False
        self.jump_grace_max_frames = kwargs.get("jump_grace_frames", 5)
        self.jump_grace_frames = 0
        self.knockback_speed = kwargs.get("knockback_speed", pygame.Vector2(200, 500))
        self.damage_knockback_speed = kwargs.get("damage_knockback_speed", 10)

        # Setup colliders
        self.collider_offset = kwargs.get("collider_offset", pygame.Vector2(0,0))
        self.collider_size = kwargs.get("collider_size", pygame.Vector2(0,0))
        
        # Setup damage colliders
        self.attack0_length = kwargs.get("attack0_length", 100)
        self.attack0_width = kwargs.get("attack0_width", 50)
        self.attack1_length = kwargs.get("attack1_length", 100)
        self.attack1_width = kwargs.get("attack1_width", 50)
        self.attack2_length = kwargs.get("attack2_length", 100)
        self.attack2_width = kwargs.get("attack2_width", 50)

        # Other
        self.hearts = kwargs.get("hearts", 3)
        self.iframe_length = kwargs.get("iframes", 120)
        self.transition_max_frames = kwargs.get("transition_frames", 120)
        self.transition_frames = 0
        self.transition = None
        self.water_splash_json_filename = kwargs.get("water_splash_json_filename", None)
        if not self.water_splash_json_filename == None:
            self.water_splash = Sprite.AnimatedSprite(spritesheet_json_filename=self.water_splash_json_filename, spritesheet_scale=(0.5,0.5))
        self.water_big_splash_json_filename = kwargs.get("water_big_splash_json_filename", None)
        if not self.water_big_splash_json_filename == None:
            self.water_big_splash = Sprite.AnimatedSprite(spritesheet_json_filename=self.water_big_splash_json_filename, spritesheet_scale=(0.5,0.5))
        
        self.short_stop_json_filename = kwargs.get("short_stop_json_filename", None)
        if not self.short_stop_json_filename == None:
            self.short_stop = Sprite.AnimatedSprite(spritesheet_json_filename=self.short_stop_json_filename, calculate_flip=True, spritesheet_scale=(0.5,0.5))
        self.hard_stop_json_filename = kwargs.get("hard_stop_json_filename", None)
        if not self.hard_stop_json_filename == None:
            self.hard_stop = Sprite.AnimatedSprite(spritesheet_json_filename=self.hard_stop_json_filename, calculate_flip=True, spritesheet_scale=(0.5,0.5))
            self.hard_stop1 = Sprite.AnimatedSprite(spritesheet_json_filename=self.hard_stop_json_filename, calculate_flip=True, spritesheet_scale=(0.5,0.5))
            self.hard_stop1.flipX = True
        

        self.velocity = pygame.Vector2(0, 0)
        self.constant_velocity = pygame.Vector2(0, 0)
        self.collider = pygame.Rect(
            self.position.x+self.collider_offset.x, 
            self.position.y+self.collider_offset.y, 
            self.collider_size.x, 
            self.collider_size.y
        )
        self.floor_collider = pygame.Rect(
            self.position.x+self.collider_offset.x+self.collider_size.x/4, 
            self.position.y+self.collider_offset.y+(self.collider_size.y-1), 
            self.collider_size.x/2, 
            1
        )
        self.is_on_ground = False
        self.key_state = {"up":False, "down":False, "right":False, "left":False, "jump":False, "attack":False}
        self.state = "idle"
        self.iframes = 0
        self.is_in_water = False
        self.can_save = False
        self.can_attack = True
        self.save_level = 0

        if "spritesheet_json_filename" in kwargs:
            self.play_animation("idle", loop=True)

    def get_attack_colliders(self):
        """ """
        if self.can_attack and self.animation_playing:
            if self.animation_name == "attack0" and self.frame_num >= 5:
                inflated = self.collider.inflate(self.attack0_length, self.attack0_width)
                return [inflated.move( (((not self.flipX)*2) - 1)*(self.attack0_length/2 + self.collider_size.x/2), 0)]

            if self.animation_name == "attack1" and self.frame_num == 4:
                inflated = self.collider.inflate(self.attack1_width, self.attack1_length)
                return [inflated.move(0, -self.attack1_length/2 -self.collider_size.y/2)]

            if self.animation_name == "attack2" and self.frame_num < 5:
                inflated = self.collider.inflate(self.attack2_width, self.attack1_length)
                return [inflated.move(0, self.attack1_length/2 +self.collider_size.y/2)]

    def render_colliders(self, delta, surface, offset):
        """

        :param delta: 
        :param surface: 
        :param offset: 

        """
        dirty_rects = []

        collider = self.collider.move(offset)
        pygame.draw.rect(surface, (0,255,0), collider)
        dirty_rects.append(collider)

        floor_collider = self.floor_collider.move(offset)
        pygame.draw.rect(surface, (255,255,0), floor_collider)
        dirty_rects.append(floor_collider)

        if self.can_attack:
            if self.animation_name == "attack0" and self.frame_num >= 5:
                attack_collider = collider.inflate(self.attack0_length, self.attack0_width)
                attack_collider.move_ip( (((not self.flipX)*2) - 1)*(self.attack0_length/2 + self.collider_size.x/2), 0)
                pygame.draw.rect(surface, (0,0,255), attack_collider)
                dirty_rects.append(attack_collider)

            if self.animation_name == "attack1" and self.frame_num == 4:
                attack_collider = collider.inflate(self.attack1_width, self.attack1_length)
                attack_collider.move_ip(0, -self.attack1_length/2 -self.collider_size.y/2)
                pygame.draw.rect(surface, (0,0,255), attack_collider)
                dirty_rects.append(attack_collider)

            if self.animation_name == "attack2":
                attack_collider = collider.inflate(self.attack2_width, self.attack2_length)
                attack_collider.move_ip(0, self.attack1_length/2 +self.collider_size.y/2)
                pygame.draw.rect(surface, (0,0,255), attack_collider)
                dirty_rects.append(attack_collider)
        return dirty_rects

    def physics_process(self, delta, colliders = None, damage_colliders=None, hitable_colliders=None, death_colliders=None, save_colliders=None, water_colliders=None, transitions=None, hit_occured=False, allow_movement=True):
        """

        :param delta: 
        :param colliders:  (Default value = None)
        :param damage_colliders:  (Default value = None)
        :param hitable_colliders:  (Default value = None)
        :param death_colliders:  (Default value = None)
        :param save_colliders:  (Default value = None)
        :param water_colliders:  (Default value = None)
        :param transitions:  (Default value = None)
        :param hit_occured:  (Default value = False)
        :param allow_movement: (Defulat value = True)

        """
        level_state_changes = {"reset":False, "transition":None, "respawn":False, "hit":False}

        # Dust states
        hard_landing, soft_landing, hard_turn = False, False, False

        # Check for transition events
        if not transitions == None and self.transition_frames == 0:
            collision = self.collider.collidelist([d["collider"] for d in transitions])
            if not collision == -1:
                self.transition = transitions[collision]
                self.transition_frames = self.transition_max_frames
                if self.transition["direction"] == "N":
                    self.velocity = self.velocity.length() * pygame.Vector2(0,1)
                    Settings.SOUND_EFFECTS["jump"].Play(fade_in_ms=200)
                    self.play_animation("idle")
                elif self.transition["direction"] == "S":
                    self.velocity = self.velocity.length() * pygame.Vector2(0,-1)
                    Settings.SOUND_EFFECTS["falling"].Play(fade_in_ms=200)
                    self.play_animation("idle")
                elif self.transition["direction"] == "E":
                    self.constant_velocity = pygame.Vector2(-self.walk_speed, 0)
                    self.play_animation("walk")
                    Settings.SOUND_EFFECTS["run"].Play(fade_in_ms=200)
                elif self.transition["direction"] == "W":
                    self.constant_velocity = pygame.Vector2(self.walk_speed, 0)
                    Settings.SOUND_EFFECTS["run"].Play(fade_in_ms=200)
                    self.play_animation("walk")
        
        if self.transition_frames > 0:
            self.transition_frames -= 1
            if self.transition_frames == 0:
                level_state_changes["transition"] = self.transition
            if not self.transition == None and (self.transition["direction"] == "E" or self.transition["direction"] == "W"):
                # Apply forces
                if not self.velocity == pygame.Vector2(0,0):
                    self.velocity -= self.velocity * delta * self.air_resistance
                self.velocity += delta * self.gravity
        else:
            if self.jump_grace_frames > 0:
                self.jump_grace_frames-=1

            if not water_colliders == None:
                    collisions = self.collider.collidelist(water_colliders)
                    if not collisions == -1:
                        collision = water_colliders[collisions]
                        if not self.is_in_water:
                            self.water_big_splash.play_animation("loop")
                            water_rect = self.water_big_splash.animations_data[self.water_big_splash.animation_index]["frames"][0].get_rect()
                            self.water_big_splash.position = pygame.Vector2(
                                self.position.x + self.collider_offset.x + self.collider_size.x / 2 - water_rect.width / 2,
                                collision.top - water_rect.height,
                            )
                        else:
                            if not self.water_splash.animation_playing and abs(self.constant_velocity.x) > 0:
                                self.water_splash.play_animation("loop")
                                water_rect = self.water_big_splash.animations_data[self.water_splash.animation_index]["frames"][0].get_rect()
                                self.water_splash.position = pygame.Vector2(
                                    self.position.x + self.collider_offset.x + self.collider_size.x / 2 - water_rect.width / 2,
                                    collision.top - water_rect.height,
                                )
                        self.is_in_water = True
                    else:
                        self.is_in_water = False
            else:
                self.is_in_water = False

            attack_colliders = self.get_attack_colliders()
            collision = False
            if not attack_colliders == None:
                for attack in attack_colliders:
                    collision = collision or (not attack.collidelist(hitable_colliders) == -1)
            
            if hit_occured or collision:
                self.can_attack = False
                if self.animation_name == "attack0":
                    self.velocity.x = (self.flipX*2 - 1)*self.knockback_speed.x
                elif self.animation_name == "attack1" and not self.is_on_ground:
                    self.velocity.y = self.knockback_speed.y
                elif self.animation_name == "attack2":
                    self.velocity.y = -self.knockback_speed.y

            self.is_white = False
            if not self.iframes == 0 and not self.animation_name == "death":
                self.iframes -= 1

                flash_distribution = [1,1,1,1,0,1,1,1,0,0,1,1,0,0,0,1,0,0,0]
                if flash_distribution[int(((self.iframe_length - self.iframes) / self.iframe_length)*(len(flash_distribution)-1))]:
                    self.is_white = True

            if (not (self.animation_name == "sit" or self.animation_name == "unsit" or self.animation_name == "death") or (self.animation_finished and not self.animation_name == "sit")) and allow_movement:
                if not self.key_state["left"] == self.key_state["right"]:
                    if self.key_state["right"]:
                        self.flipX = False

                        if self.constant_velocity.x < 0:
                            hard_turn = True

                        if self.is_in_water:
                            self.constant_velocity.x = self.water_walk_speed
                        else:
                            self.constant_velocity.x = self.walk_speed

                        if self.animation_name == "idle" or not self.animation_playing:
                            self.play_animation("walk", loop=True)

                        
                    elif self.key_state["left"]:
                        self.flipX = True

                        if self.constant_velocity.x > 0:
                            hard_turn = True

                        if self.is_in_water:
                            self.constant_velocity.x = -self.water_walk_speed
                        else:
                            self.constant_velocity.x = -self.walk_speed

                        if self.animation_name == "idle" or not self.animation_playing:
                            self.play_animation("walk", loop=True)
                else:
                    self.constant_velocity.x = 0
                    if self.animation_name == "walk" or not self.animation_playing:
                        self.play_animation("idle", loop=True)     
            else:
                self.constant_velocity.x = 0       
                if (not allow_movement) and (self.animation_name == "walk" or not self.animation_playing):
                    self.play_animation("idle", loop=True)     

            # Apply forces
            if not self.velocity == pygame.Vector2(0,0):
                if self.is_in_water:
                    self.velocity -= self.velocity * delta * self.water_resistance
                    self.velocity.y -= delta * random.randrange(0, self.gravity.y*1.5*100) / 100
                elif self.is_on_ground:
                    self.velocity -= self.velocity * delta * self.floor_resistance
                else:
                    self.velocity -= self.velocity * delta * self.air_resistance

            self.velocity += delta * self.gravity

            # Handle held jump velocity
            if (self.jumping and not self.key_state["jump"]) or self.jump_add_time > self.jump_add_max_time:
                self.jumping = False
            
            if self.jumping:
                self.jump_add_time += delta
                self.velocity.y += delta * self.jump_add_speed

        old_position = copy.deepcopy(self.position)
        self.position += (self.velocity + self.constant_velocity) * delta

        self.collider.x = self.position.x + self.collider_offset.x
        self.collider.y = self.position.y + self.collider_offset.y
        self.floor_collider.x = self.position.x + self.collider_offset.x + self.collider_size.x/4
        self.floor_collider.y = self.position.y + self.collider_offset.y + self.collider_size.y

        if not colliders == None:
            collision = self.floor_collider.collidelist(colliders)
            if not collision == -1:
                if self.is_on_ground == False:
                    if self.velocity.y > 200:
                        hard_landing = True
                    elif self.velocity.y > 10:
                        soft_landing = True

                self.is_on_ground = True
                
                self.jump_grace_frames = self.jump_grace_max_frames
            else:
                self.is_on_ground = False
            for collider in colliders:
                if self.collider.colliderect(collider):
                    # Mininmise all translations
                    push_y = min(
                        # Consider moving down; Hit the top side
                        collider.top - self.collider.height - self.collider_offset.y - self.position.y+1,
                        # Consider moving up; Hit the bottom side
                        collider.bottom - self.collider_offset.y - self.position.y,
                        key=abs
                    )
                    push_x = min(
                        # Consider moving right; Hit the left side
                        collider.left - self.collider.width - self.collider_offset.x - self.position.x,
                        # Consider moving left; Hit the right side
                        collider.right - self.collider_offset.x - self.position.x,
                        key=abs
                    )

                    # Combat high velocities passing through thin colliders, note: fails when v*dt > size
                    if abs(self.velocity.x*delta) > self.collider.width / 2:
                        if self.velocity.x > 0:
                            push_x = collider.left - self.collider.width - self.collider_offset.x - self.position.x
                        else:
                            push_x = collider.right - self.collider_offset.x - self.position.x
                    
                    if abs(self.velocity.y*delta) > self.collider.height / 2:
                        if self.velocity.y > 0:
                            push_y = collider.top - self.collider.height - self.collider_offset.y - self.position.y+1
                        else:
                            push_y = collider.bottom - self.collider_offset.y - self.position.y

                    # Choose smaller transformation
                    if abs(push_x) < abs(push_y):
                        self.position.x = push_x + self.position.x
                        if push_x > 0 and self.velocity.x < 0:
                            self.velocity.x = 0
                        elif push_x < 0 and self.velocity.x > 0:
                            self.velocity.x = 0
                    else:
                        self.position.y = push_y + self.position.y
                        if push_y > 0 and self.velocity.y < 0:
                            self.velocity.y = 0
                        elif push_y < 0 and self.velocity.y > 0:
                            self.velocity.y = 0
        else:
            self.is_on_ground = False

        # Check for damage events
        if not damage_colliders == None and self.iframes == 0 and not self.animation_name == "death":
            collision = self.collider.collidelist(damage_colliders)
            if not collision == -1:
                level_state_changes["hit"] = True
                self.iframes = self.iframe_length
                self.play_animation("damage")
                self.hearts -= 1
                
                # Apply knockback
                s = pygame.Vector2(
                    damage_colliders[collision].left+damage_colliders[collision].width/2, 
                    damage_colliders[collision].top+damage_colliders[collision].height/2,
                ) - (self.position + self.collider_offset + self.collider_size/2)
                self.velocity.x = self.velocity.x + self.damage_knockback_speed*(int(s.x < 0)*2 - 1)
                self.velocity.y = self.velocity.y + self.damage_knockback_speed*(int(s.y < 0)*2 - 1)


        # Check for death events
        if not death_colliders == None and not self.animation_name == "death":
            collision = self.collider.collidelist(death_colliders)
            if not collision == -1:
                self.hearts -= 1
                level_state_changes["reset"] = True

        if self.hearts == 0 and not self.animation_name == "death":
            level_state_changes["respawn"] = True
        
        # Check for save possibility
        self.can_save = False
        if not save_colliders == None:
            collision = self.collider.collidelist(save_colliders)
            if not collision == -1:
                self.can_save = True

        # Create dust trails
        if self.is_on_ground and abs((self.position - old_position).x) > 1:
            if not hard_turn and not self.short_stop.animation_playing:
                self.short_stop.play_animation("loop")
                stop_rect = self.short_stop.animations_data[self.short_stop.animation_index]["frames"][0].get_rect()

                self.short_stop.flipX = self.flipX
                if self.flipX:
                    self.short_stop.position = pygame.Vector2(
                        self.position.x + self.collider_size.x + self.collider_offset.x - stop_rect.width,
                        self.position.y + self.collider_offset.y + self.collider_size.y - stop_rect.height,
                    )
                else:
                    self.short_stop.position = pygame.Vector2(
                        self.position.x + self.collider_offset.x,
                        self.position.y + self.collider_offset.y + self.collider_size.y - stop_rect.height,
                    )
            elif hard_turn and not self.hard_stop.animation_playing:
                self.hard_stop.play_animation("loop")
                stop_rect = self.hard_stop.animations_data[self.hard_stop.animation_index]["frames"][0].get_rect()

                self.hard_stop.flipX = self.flipX
                if self.flipX:
                    self.hard_stop.position = pygame.Vector2(
                        self.position.x + self.collider_size.x + self.collider_offset.x - stop_rect.width,
                        self.position.y + self.collider_offset.y + self.collider_size.y - stop_rect.height,
                    )
                else:
                    self.hard_stop.position = pygame.Vector2(
                        self.position.x + self.collider_offset.x,
                        self.position.y + self.collider_offset.y + self.collider_size.y - stop_rect.height,
                    )

        if hard_landing and not self.hard_stop1.animation_playing:
            self.hard_stop.play_animation("loop")
            self.hard_stop1.play_animation("loop")
            stop_rect = self.hard_stop.animations_data[self.hard_stop.animation_index]["frames"][0].get_rect()

            self.hard_stop.flipX = False
            self.hard_stop.position = pygame.Vector2(
                self.position.x + self.collider_size.x + self.collider_offset.x - stop_rect.width,
                self.position.y + self.collider_offset.y + self.collider_size.y - stop_rect.height,
            )
            self.hard_stop1.position = pygame.Vector2(
                self.position.x + self.collider_offset.x,
                self.position.y + self.collider_offset.y + self.collider_size.y - stop_rect.height,
            )
        
        if self.transition == None:
            # Create sounds
            if self.velocity.y > 100 and not self.is_on_ground and not Settings.SOUND_EFFECTS["falling"].IsPlaying():
                Settings.SOUND_EFFECTS["falling"].Play(fade_in_ms=200)
            else:
                Settings.SOUND_EFFECTS["falling"].Stop(fade_out_ms=100)
            
            if abs(self.constant_velocity.x) > 0 and self.is_on_ground:
                if self.is_in_water:
                    Settings.SOUND_EFFECTS["run"].Stop()
                    if not Settings.SOUND_EFFECTS["swim"].IsPlaying():
                        Settings.SOUND_EFFECTS["swim"].Play(fade_in_ms=700)
                else:
                    Settings.SOUND_EFFECTS["swim"].Stop(fade_out_ms=400)
                    if not Settings.SOUND_EFFECTS["run"].IsPlaying():
                        Settings.SOUND_EFFECTS["run"].Play()
            else:
                Settings.SOUND_EFFECTS["swim"].Stop(fade_out_ms=400)
                Settings.SOUND_EFFECTS["run"].Stop()

            if (hard_landing or soft_landing) and self.is_in_water:
                Settings.SOUND_EFFECTS["land_splash"].Play(fade_in_ms=100)
            elif hard_landing:
                Settings.SOUND_EFFECTS["land_hard"].Play(fade_in_ms=200)
            elif soft_landing:
                Settings.SOUND_EFFECTS["land_soft"].Play(fade_in_ms=200)
            
                
            if level_state_changes["hit"] or level_state_changes["reset"]:
                Settings.SOUND_EFFECTS["damage"].Play(fade_in_ms=200)
            if level_state_changes["respawn"] or level_state_changes["respawn"]:
                if not Settings.SOUND_EFFECTS["death"].IsPlaying():
                    Settings.SOUND_EFFECTS["death"].Play(fade_in_ms=200)

        return level_state_changes

    def update_animation(self, delta):
        """

        :param delta: 

        """
        super().update_animation(delta)

        self.water_big_splash.update_animation(delta)
        self.water_splash.update_animation(delta)

        self.short_stop.update_animation(delta)
        self.hard_stop.update_animation(delta)
        self.hard_stop1.update_animation(delta)

    def render(self, surface, offset=pygame.Vector2(0,0), size=None, delta=None):
        """

        :param surface: 
        :param offset:  (Default value = pygame.Vector2(0, 0)
        :param size:  (Default value = None)
        :param delta:  (Default value = None)

        """
        if not delta == None:
            self.update_animation(delta)
        dirty_rects = super().render(surface, offset, size)

        dirty_rects += self.water_big_splash.render(surface, offset, size)
        dirty_rects += self.water_splash.render(surface, offset, size)

        dirty_rects += self.short_stop.render(surface, offset, size)
        dirty_rects += self.hard_stop.render(surface, offset, size)
        dirty_rects += self.hard_stop1.render(surface, offset, size)
        
        return dirty_rects

    def input(self, events):
        """

        :param events: 

        """
        save = False
        def reenable_attack(self):
            """ """
            self.can_attack = True
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["up"]): 
                    if self.animation_name == "sit":
                        self.play_animation("unsit")
                    
                    self.key_state["up"] = True
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["down"]): 
                    self.key_state["down"] = True
                    if self.can_save and (not self.animation_name == "death"):
                        if self.animation_name == "sit":
                            self.play_animation("unsit")
                        else:
                            save = True
                            self.velocity = pygame.Vector2(0,0)
                            self.constant_velocity = pygame.Vector2(0,0)
                            self.play_animation("sit")
                    else:
                        if self.animation_name == "attack0" and self.frame_num < 4:
                            Settings.SOUND_EFFECTS["attack"].Stop(fade_out_ms=100)
                            Settings.SOUND_EFFECTS["big_attack"].Play(fade_in_ms=200)
                            self.play_animation("attack2")
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["attack"]):
                    if self.animation_name == "sit":
                            self.play_animation("unsit")
                    else:
                        self.key_state["attack"] = True    
                        if not self.animation_name == "death":
                            if self.key_state["down"] and not self.is_on_ground and (not self.animation_name == "death"):
                                if not (self.animation_name == "attack2" and self.animation_playing):
                                    self.play_animation("attack2", on_animation_end=reenable_attack, on_animation_interrupt=reenable_attack)
                                    Settings.SOUND_EFFECTS["big_attack"].Play(fade_in_ms=200)
                            elif self.key_state["up"]:
                                if not (self.animation_name == "attack1" and self.animation_playing):
                                    self.play_animation("attack1", on_animation_end=reenable_attack, on_animation_interrupt=reenable_attack)
                                    Settings.SOUND_EFFECTS["big_attack"].Play(fade_in_ms=200)
                            else:
                                if not (self.animation_name == "attack0" and self.animation_playing):
                                    self.play_animation("attack0", on_animation_end=reenable_attack, on_animation_interrupt=reenable_attack)
                                    Settings.SOUND_EFFECTS["attack"].Play(fade_in_ms=200)
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["jump"]): 
                    if self.animation_name == "sit":
                        self.play_animation("unsit")
                    else:
                        self.key_state["jump"] = True
                        if (self.is_on_ground or self.jump_grace_frames > 0) and not self.animation_name == "sit" and not (self.transition_frames > 0) and (not self.animation_name == "death"):
                            self.jumping = True
                            self.jump_add_time = 0
                            if self.iframes == 0:
                                self.play_animation("jump")
                            self.velocity.y += self.jump_speed

                            Settings.SOUND_EFFECTS["jump"].Play(fade_in_ms=200)
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["right"]): 
                    if self.animation_name == "sit":
                        self.play_animation("unsit")
                    self.key_state["right"] = True
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["left"]): 
                    if self.animation_name == "sit":
                        self.play_animation("unsit")
                    self.key_state["left"] = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["jump"]): self.key_state["jump"] = False
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["up"]): self.key_state["up"] = False
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["down"]): self.key_state["down"] = False
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["right"]): self.key_state["right"] = False
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["left"]): self.key_state["left"] = False
        return save
    def input_static(self, events):
        """

        :param events: 

        """
        for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["jump"]): self.key_state["jump"] = True
                    if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["up"]): self.key_state["up"] = True
                    if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["down"]): self.key_state["down"] = True
                    if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["right"]): self.key_state["right"] = True
                    if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["left"]): self.key_state["left"] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["jump"]): self.key_state["jump"] = False
                    if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["up"]): self.key_state["up"] = False
                    if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["down"]): self.key_state["down"] = False
                    if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["right"]): self.key_state["right"] = False
                    if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["left"]): self.key_state["left"] = False

    # https://stackoverflow.com/questions/57225611/how-to-deepcopy-object-which-contains-pygame-surface
    def copy(self):
        """ """
        copyobj = Player()
        for name, attr in self.__dict__.items():
            if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
                copyobj.__dict__[name] = attr.copy()
            else:
                copyobj.__dict__[name] = copy.deepcopy(attr)
        return copyobj