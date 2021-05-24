import pygame, json, itertools, copy, random, math

# For debugging
from Packages import Settings, Sprite

class Enemy(Sprite.AnimatedSprite):
    """ """
    def __init__(self, *args, **kwargs):
        Sprite.AnimatedSprite.__init__(self, *args, **kwargs)

        # Setup physics
        self.gravity = kwargs.get("gravity", pygame.Vector2(0,500))
        self.walk_speed = kwargs.get("walk_speed", 200)

        # Setup colliders
        self.collider_offset = kwargs.get("collider_offset", pygame.Vector2(0,0))
        self.collider_size = kwargs.get("collider_size", pygame.Vector2(0,0))
        self.weapons_collider_offset = kwargs.get("weapons_collider_offset", pygame.Vector2(0,0))
        self.weapons_collider_size = kwargs.get("weapons_collider_size", pygame.Vector2(64,64))

        # Setup state
        self.attack_distance = kwargs.get("attack_distance", self.weapons_collider_size.x + 10)
        self.platform_edge_distance = kwargs.get("platform_edge_distance", 20)
        self.alert_distance = kwargs.get("alert_distance", 90)
        self.attack_gap = kwargs.get("attack_gap_time", 0.5)
        self.attack_gap_time = kwargs.get("attack_gap_time", 0.5)
        
        self.velocity = pygame.Vector2(0, 0)
        self.collider = pygame.Rect(
            self.position.x+self.collider_offset.x, 
            self.position.y+self.collider_offset.y, 
            self.collider_size.x, 
            self.collider_size.y
        )
        self.weapons_collider = pygame.Rect(
            self.position.x+self.weapons_collider_offset.x, 
            self.position.y+self.weapons_collider_offset.y, 
            self.weapons_collider_size.x, 
            self.weapons_collider_size.y
        )
        self.weapons_collider_flip = pygame.Rect(
            self.position.x+self.weapons_collider_offset.x+self.collider_size.x, 
            self.position.y+self.weapons_collider_offset.y, 
            self.weapons_collider_size.x, 
            self.weapons_collider_size.y
        )

        # Setup state machine, expects: "patrol", "alert", "idle", "attack", "wait", "death", "dead"
        self.state = "patrol"

        if "spritesheet_json_filename" in kwargs:
            self.play_animation("walk", loop=True)

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

        if self.state == "attack" and (self.frame_num >= 2 and self.frame_num <= 5):
            if self.flipX:
                weapons_collider_flip = self.weapons_collider_flip.move(offset)
                pygame.draw.rect(surface, (0,255,255), weapons_collider_flip)
                dirty_rects.append(weapons_collider_flip)
            else:
                weapons_collider = self.weapons_collider.move(offset)
                pygame.draw.rect(surface, (0,255,255), weapons_collider)
                dirty_rects.append(weapons_collider)
        return dirty_rects

    def update_state(self, player_position=None, state=None):
        """

        :param player_position:  (Default value = None)
        :param state:  (Default value = None)

        """
        if not state == None:
            self.state = state
        elif not player_position == None and not self.state == "attack" and not self.state == "wait" and not self.state == "death" and not self.state == "dead":
            player_distance = (player_position - self.position).length()
            if player_distance < self.alert_distance:
                if not self.state == "alert":
                    self.play_animation("level_spear")
                    self.state = "alert"
                else:
                    if player_distance < self.attack_distance and ((player_position.y >= self.position.y) and (player_position.y <= self.position.y+self.collider_size.y)):
                        def handle_stab_end(self):
                            """ """
                            if self.state == "attack":
                                self.state = "wait"
                            self.attack_gap_time = 0
                        self.play_animation("stab", on_animation_end=handle_stab_end)
                        self.state = "attack"
                    else: self.state = "alert"
            elif self.state == "alert":
                self.state = "patrol"
                self.play_animation("unlevel_spear", on_animation_end=lambda self: self.play_animation("walk", loop=True))

    def physics_process(self, delta, colliders = None, player_position=None, attack_colliders=None):
        """

        :param delta: 
        :param colliders:  (Default value = None)
        :param player_position:  (Default value = None)
        :param attack_colliders:  (Default value = None)

        """
        if self.attack_gap_time < self.attack_gap:
            self.attack_gap_time += delta
            if self.attack_gap_time >= self.attack_gap:
                self.state = "alert"


        if self.state == "patrol":
            self.velocity.x = ((not self.flipX)*2 - 1)*self.walk_speed
        else:
            self.velocity.x = 0
            if self.animation_name == "walk":
                    self.play_animation("idle", loop=True)

            # Make sure entity is facing the correct direction
            if not self.state == "attack": 
                self.flipX = (player_position - self.position).x < 0

        self.velocity += delta * self.gravity
        self.position += self.velocity * delta

        self.collider.x = self.position.x + self.collider_offset.x
        self.collider.y = self.position.y + self.collider_offset.y
        self.weapons_collider.x = self.position.x + self.weapons_collider_offset.x + self.collider_size.x + self.weapons_collider_size.x
        self.weapons_collider.y = self.position.y + self.weapons_collider_offset.y
        self.weapons_collider_flip.x = self.position.x + self.weapons_collider_offset.x
        self.weapons_collider_flip.y = self.weapons_collider.y

        # Check for damage events
        is_damaged = False
        if not attack_colliders == None and not self.state == "death":
            collision = self.collider.collidelist(attack_colliders)
            if not collision == -1:
                self.play_animation("death", on_animation_end=lambda self: self.update_state(state="dead"), on_animation_interrupt=lambda self: self.update_state(state="dead"))
                self.state = "death"
                is_damaged = True

        if not colliders == None:
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

                    # Check how close entity is to edge
                    if abs(push_x) < self.platform_edge_distance:
                        # Switch direction
                        if push_x > 0:
                            self.flipX = True
                        else:
                            self.flipX = False

                    # Choose smaller transformation
                    if abs(push_x) < abs(push_y):
                        self.position.x = push_x + self.position.x
                    else:
                        self.position.y = push_y + self.position.y
                        self.velocity.y = 0
        return is_damaged
        
        
                    
    def get_damage_colliders(self):
        """ """
        colliders = [self.collider]
        if self.state == "attack" and (self.frame_num >= 2 and self.frame_num <= 5):
            if self.flipX:
                colliders.append(self.weapons_collider_flip)
            else:
                colliders.append(self.weapons_collider)

        return colliders
    
    # https://stackoverflow.com/questions/57225611/how-to-deepcopy-object-which-contains-pygame-surface
    def copy(self):
        """ """
        copyobj = Enemy()
        for name, attr in self.__dict__.items():
            if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
                copyobj.__dict__[name] = attr.copy()
            else:
                copyobj.__dict__[name] = copy.deepcopy(attr)

        return copyobj

class FlyingEnemy(Sprite.AnimatedSprite):
    """ """
    def __init__(self, *args, **kwargs):
        Sprite.AnimatedSprite.__init__(self, *args, **kwargs)

        # Setup colliders
        self.collider_offset = kwargs.get("collider_offset", pygame.Vector2(0,0))
        self.collider_size = kwargs.get("collider_size", pygame.Vector2(0,0))

        # Setup state
        self.og_position = pygame.Vector2(0,0)
        self.drift_speed = kwargs.get("drift_speed", 10)
        self.attack_acceleration = kwargs.get("attack_acceleration", 5)
        self.max_speed = kwargs.get("max_speed", 200)
        self.max_attack_speed = kwargs.get("max_attack_speed", 500)
        self.max_drift_distance = kwargs.get("max_drift_distance", 10)
        self.alert_distance = kwargs.get("alert_distance", 100)
        self.attack_position = pygame.Vector2(0,0)

        self.velocity = pygame.Vector2(0, 0)
        self.collider = pygame.Rect(
            self.position.x+self.collider_offset.x, 
            self.position.y+self.collider_offset.y, 
            self.collider_size.x, 
            self.collider_size.y
        )
        
        self.state = "idle"

        if "spritesheet_json_filename" in kwargs:
            self.play_animation("fly", loop=True)

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

        return dirty_rects

    def update_state(self, player_position=None, state=None):
        """

        :param player_position:  (Default value = None)
        :param state:  (Default value = None)

        """
        if not state is None:
            self.state = state
        elif not (self.state == "death" or self.state == "dead"):
            if (self.position - player_position).length() < self.alert_distance:
                self.state = "alert"
                self.attack_position = player_position
            else:
                self.state = "idle"
                self.og_position = self.position

    def physics_process(self, delta, colliders = None, player_position=None, attack_colliders=None):
        """

        :param delta: 
        :param colliders:  (Default value = None)
        :param player_position:  (Default value = None)
        :param attack_colliders:  (Default value = None)

        """
        is_damaged = False
        self.flipX = self.velocity.x < 0
        if not (self.state == "death" or self.state == "dead"):
            if self.state == "alert":
                rand_vel_x = random.randrange(-self.drift_speed*100, self.drift_speed*100)/1000
                rand_vel_y = random.randrange(-self.drift_speed*100, self.drift_speed*100)/1000
                self.velocity += pygame.Vector2(rand_vel_x, rand_vel_y)
                self.velocity += pygame.Vector2(self.attack_position - self.position).normalize() * self.attack_acceleration

                if self.velocity.length() > self.max_attack_speed:
                    self.velocity = self.velocity.normalize()*self.max_attack_speed
                self.position += self.velocity * delta
            else:
                rand_vel_x = random.randrange(-self.drift_speed*100, self.drift_speed*100)/100
                rand_vel_y = random.randrange(-self.drift_speed*100, self.drift_speed*100)/100
                self.velocity += pygame.Vector2(rand_vel_x, rand_vel_y)

                if self.position.x - self.og_position.x >= self.max_drift_distance:
                    self.velocity.x = min(self.velocity.x, 0)
                elif self.position.x - self.og_position.x <= -self.max_drift_distance:
                    self.velocity.x = max(self.velocity.x, 0)
                if self.position.y - self.og_position.y >= self.max_drift_distance:
                    self.velocity.y = min(self.velocity.y, 0)
                elif self.position.y - self.og_position.y <= -self.max_drift_distance:
                    self.velocity.y = max(self.velocity.y, 0)
                
                if self.velocity.length() > self.max_speed:
                    self.velocity = self.velocity.normalize()*self.max_speed
                self.position += self.velocity * delta


            self.collider.x = self.position.x + self.collider_offset.x
            self.collider.y = self.position.y + self.collider_offset.y

            # Check for damage events
            is_damaged = False
            if not attack_colliders == None:
                generous_collider = self.collider.inflate(1.2,1.2)
                collision = generous_collider.collidelist(attack_colliders)
                if not collision == -1:
                    self.play_animation("death", on_animation_end=lambda self: self.update_state(state="dead"), on_animation_interrupt=lambda self: self.update_state(state="dead"))
                    self.state = "death"
                    is_damaged = True

            if not colliders == None:
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

                        # Choose smaller transformation
                        if abs(push_x) < abs(push_y):
                            self.position.x = push_x + self.position.x
                            if push_x > 0:
                                self.velocity.x = abs(self.velocity.x) / 2
                            else:
                                self.velocity.x = -abs(self.velocity.x) / 2
                        else:
                            self.position.y = push_y + self.position.y
                            if push_y > 0:
                                self.velocity.y = abs(self.velocity.y) / 2
                            else:
                                self.velocity.y = -abs(self.velocity.y) / 2
            self.update_state(player_position)
        return is_damaged
                    
    def get_damage_colliders(self):
        """ """
        if not self.state == "death":
            return [self.collider]
        return []
    
    # https://stackoverflow.com/questions/57225611/how-to-deepcopy-object-which-contains-pygame-surface
    def copy(self):
        """ """
        copyobj = FlyingEnemy()
        for name, attr in self.__dict__.items():
            if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
                copyobj.__dict__[name] = attr.copy()
            else:
                copyobj.__dict__[name] = copy.deepcopy(attr)

        return copyobj

class ChallengeCollectable(Sprite.AnimatedSprite):
    """ """
    def __init__(self, *args, **kwargs):
        Sprite.AnimatedSprite.__init__(self, *args, **kwargs)

        # Setup colliders
        self.collider_offset = kwargs.get("collider_offset", pygame.Vector2(0,0))
        self.collider_size = kwargs.get("collider_size", pygame.Vector2(0,0))

        # Setup state
        self.og_position = kwargs.get("position", pygame.Vector2(0,0))
        self.float_period = kwargs.get("float_period", 2)
        self.max_float_distance = kwargs.get("max_float_distance", 10)
        self.float_time = 0

        self.collider = pygame.Rect(
            self.position.x+self.collider_offset.x, 
            self.position.y+self.collider_offset.y, 
            self.collider_size.x, 
            self.collider_size.y
        )
        
        self.state = "loop"

        if "spritesheet_json_filename" in kwargs:
            self.play_animation("loop", loop=True)

    def render_colliders(self, delta, surface, offset):
        """

        :param delta: 
        :param surface: 
        :param offset: 

        """
        dirty_rects = []

        collider = self.collider.move(offset)
        pygame.draw.rect(surface, (0,255,120), collider)
        dirty_rects.append(collider)

        return dirty_rects
    def update_state(self, state=None):
        """

        :param state:  (Default value = None)

        """
        if not state is None:
            self.state = state
    def physics_process(self, delta, player_collider=None):
        """

        :param delta: 
        :param colliders:  (Default value = None)
        :param player_position:  (Default value = None)
        :param attack_colliders:  (Default value = None)

        """
        if not (self.state == "death" or self.state == "dead"):
            self.float_time += delta
            self.position = self.og_position + pygame.Vector2(0, self.max_float_distance) * math.sin(self.float_time / self.float_period)

            self.collider.x = self.position.x + self.collider_offset.x
            self.collider.y = self.position.y + self.collider_offset.y

            # Check for damage events
            if not player_collider == None:
                if self.collider.colliderect(player_collider):
                    self.play_animation("death", on_animation_end=lambda self: self.update_state(state="dead"), on_animation_interrupt=lambda self: self.update_state(state="dead"))
                    self.state = "death"
        return self.state == "dead"
                    
    # https://stackoverflow.com/questions/57225611/how-to-deepcopy-object-which-contains-pygame-surface
    def copy(self):
        """ """
        copyobj = ChallengeCollectable()
        for name, attr in self.__dict__.items():
            if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
                copyobj.__dict__[name] = attr.copy()
            else:
                copyobj.__dict__[name] = copy.deepcopy(attr)

        return copyobj