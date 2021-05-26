import pygame, copy, random, math

# For debugging
from Packages import Sprite

class Enemy(Sprite.AnimatedSprite):
    """ Standard patrolling enemy which attempts to attack player. Inherits from Sprite.AnimatedSprite.
    
    Args:
        position (pygame.Vector2): level space position of sprite.
        spritesheet_json_filename (Str): string path of json for animation.
        spritesheet_scale (tuple): x, y to scale spritesheet resolution by.
        gravity (pygame.Vector2): x, y components of constant acceleration.
        walk_speed (float): Constant speed applied when enemy is patrolling.
        collider_offset (pygame.Vector2): x, y components of offset between collider and sprite.
        collider_size (pygame.Vector2): x, y components of size of collider.
        weapons_collider_offset (pygame.Vector2): x, y components of offset between collider of attack and sprite.
        weapons_collider_size (pygame.Vector2): x, y components of size of collider of attack.
        attack_distance (float): Distance between player and enemy required for enemy to attack.
        platform_edge_distance (float): Distance between enemy collider and end of floor to turn around.
        alert_distance (float): Distance between player and enemy required for enemy to stop moving and enter alert state.
        attack_gap_time (float): Time between possible attacks by enemy.
    """
    def __init__(self, *args, **kwargs):
        # Inherit from AnimatedSprite for animations
        kwargs["calculate_flip"] = True
        kwargs["calculate_white"] = False
        Sprite.AnimatedSprite.__init__(self, *args, **kwargs)

        # Setup physics
        self.gravity = kwargs.get("gravity", pygame.Vector2(0,500))
        self.walk_speed = kwargs.get("walk_speed", 200)
        self.velocity = pygame.Vector2(0, 0)

        # Setup enemy and attack colliders
        self.collider_offset = kwargs.get("collider_offset", pygame.Vector2(0,0))
        self.collider_size = kwargs.get("collider_size", pygame.Vector2(0,0))
        self.weapons_collider_offset = kwargs.get("weapons_collider_offset", pygame.Vector2(0,0))
        self.weapons_collider_size = kwargs.get("weapons_collider_size", pygame.Vector2(64,64))

        # Actually create each collider
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

        # Setup state
        self.attack_distance = kwargs.get("attack_distance", self.weapons_collider_size.x + 10)
        self.platform_edge_distance = kwargs.get("platform_edge_distance", 20)
        self.alert_distance = kwargs.get("alert_distance", 90)
        self.attack_gap = kwargs.get("attack_gap_time", 0.5)
        self.attack_gap_time = kwargs.get("attack_gap_time", 0.5)
        

        # Setup state machine, expects: "patrol", "alert", "idle", "attack", "wait", "death", "dead"
        self.state = "patrol"

        if "spritesheet_json_filename" in kwargs:
            self.play_animation("walk", loop=True)

    def render_colliders(self, surface, offset):
        """Draw current attack and enemy colliders to level space for debuging.
        Returns list of dirty rects which have been rendered to.

        Args:
            surface (pygame.Surface): Surface to render to
            offset (pygame.Vector2): Camera offset
        """
        dirty_rects = []

        collider = self.collider.move(offset)
        pygame.draw.rect(surface, (0,255,0), collider)
        dirty_rects.append(collider)

        # Render attack colliders
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
        """ Update enemy state and animations based on player_position

        Args:
            player_position (pygame.Vector2): Position of player in level space.
            state (str): Directly set state, if given no other state changes are enacted
        """
        if not state == None:
            self.state = state
        # Don't update state if enemy isnt patrolling, alert or idle
        elif not player_position == None and not self.state == "attack" and not self.state == "wait" and not self.state == "death" and not self.state == "dead":
            # Get vector between player and enemy, assumes offsets are approximately equal
            player_distance = (player_position - pygame.Vector2(self.collider.center)).length()

            # Test if player in alert distance
            if player_distance < self.alert_distance:
                if not self.state == "alert":
                    self.play_animation("level_spear")
                    self.state = "alert"
                else:
                    # If player in attack range perform attack otherwise freeze enemy in alert state
                    if player_distance < self.attack_distance and ((player_position.y >= self.collider.center[1]) and (player_position.y <= self.collider.center[1]+self.collider_size.y)):
                        # Define local function to reset state after attacking
                        def handle_stab_end(self):
                            # If timer state wasnt already updated disable attacks until attack_gap_time
                            if self.state == "attack":
                                self.state = "wait"
                            self.attack_gap_time = 0
                        
                        # Do stab and set state
                        self.play_animation("stab", on_animation_end=handle_stab_end)
                        self.state = "attack"
                    else: 
                        self.state = "alert"
            # Exit alert state when player leaves
            elif self.state == "alert":
                self.state = "patrol"
                self.play_animation("unlevel_spear", on_animation_end=lambda self: self.play_animation("walk", loop=True))

    def physics_process(self, delta, colliders = None, player_position=None, attack_colliders=None):
        """ Calculates physics and handles animations for enemy, doesn't update state machine except during death.
        Returns True if enemy was hit by player else False
        
        Args:
            delta (float): Constant physics tick, eg. 1 / fps (required).
            colliders ([pygame.Rect]): List of rectangles describing the levels physical colliders. 
            player_position (pygame.Vector2): Level space position of player used to face enemy towards player.
            attack_colliders ([pygame.Rect]): List of rectangles which will damage an enemy, eg. list of player attack colliders. 
        """
        is_damaged = False

        if not self.state == "death" and not self.state == "dead":
            # Handle gaps between attacks by updating timer when valid
            if self.attack_gap_time < self.attack_gap:
                self.attack_gap_time += delta
                if self.attack_gap_time >= self.attack_gap:
                    # Enter alert state where enemy can now attack
                    self.state = "alert"

            if self.state == "patrol":
                # Continue moving in direction facing when patrolling, reset horizontal velocity
                self.velocity.x = ((not self.flipX)*2 - 1)*self.walk_speed
            else:
                self.velocity.x = 0
                if self.animation_name == "walk":
                        self.play_animation("idle", loop=True)

                # Make sure entity is facing the correct direction, but dont switch during attacks
                if not self.state == "attack": 
                    self.flipX = (player_position - pygame.Vector2(self.collider.center)).x < 0

            # Apply constant gravitational acceleration using dv = a * dt
            self.velocity += delta * self.gravity

            # Apply velocities using dx = v * dt
            self.position += self.velocity * delta

            # Adjust collider positions after position change
            self.collider.topleft = (self.position + self.collider_offset).xy
            self.weapons_collider.topleft = (self.position + self.weapons_collider_offset).xy
            self.weapons_collider.x = self.position.x + self.weapons_collider_offset.x + self.collider_size.x + self.weapons_collider_size.x
            self.weapons_collider.y = self.position.y + self.weapons_collider_offset.y

            # Check for damage events if not already dying
            if not attack_colliders == None:
                collision = self.collider.collidelist(attack_colliders)
                if not collision == -1:
                    # Play death animation then actually delete object
                    self.play_animation("death", 
                        on_animation_end=lambda self: self.update_state(state="dead"), 
                        on_animation_interrupt=lambda self: self.update_state(state="dead")
                    )
                    self.state = "death"
                    is_damaged = True

            if not colliders == None:
                for collider in colliders:
                    if self.collider.colliderect(collider):
                        # Use simple collision system which minimizes tranformations since enemies have low velocities
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
                            # Horizontal velocity is reset every physic tick anyway
                        else:
                            self.position.y = push_y + self.position.y
                            self.velocity.y = 0
        return is_damaged
                    
    def get_damage_colliders(self):
        """ Returns a list of pygame.Rects which represent the enemies attack hitboxes"""

        colliders = []

        # Cause damage if player walks into enemy
        if not self.state == "death" and not self.state == "dead":
            colliders.append(self.collider)

        # Add attack colliders if valid
        if self.state == "attack" and (self.frame_num >= 2 and self.frame_num <= 5):
            if self.flipX:
                colliders.append(self.weapons_collider_flip)
            else:
                colliders.append(self.weapons_collider)

        return colliders
    
    # https://stackoverflow.com/questions/57225611/how-to-deepcopy-object-which-contains-pygame-surface
    def copy(self):
        """ Standard copy constructor for complex objects """
        copyobj = Enemy()
        for name, attr in self.__dict__.items():
            if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
                copyobj.__dict__[name] = attr.copy()
            else:
                copyobj.__dict__[name] = copy.deepcopy(attr)

        return copyobj

class FlyingEnemy(Sprite.AnimatedSprite):
    """ Floating enemy with simple ai which attempts to charge player. Inherits from Sprite.AnimatedSprite. 
    
    Args:
        position (pygame.Vector2): level space position of sprite.
        spritesheet_json_filename (Str): string path of json for animation.
        spritesheet_scale (tuple): x, y to scale spritesheet resolution by.
        drift_acceleration (float): Maximum acceleration experience when velocity randomly added while drifting.
        attack_acceleration (float): Acceleration of enemy towards player while attacking.
        max_speed (float): Maximum flying speed when randomly drifting.
        max_attack_speed (float): Maximum flying speed when attacking player.
        collider_offset (pygame.Vector2): x, y components of offset between collider and sprite.
        collider_size (pygame.Vector2): x, y components of size of collider.
    """
    def __init__(self, *args, **kwargs):
        # Inherit from AnimatedSprite for animations
        kwargs["calculate_flip"] = True
        kwargs["calculate_white"] = False
        Sprite.AnimatedSprite.__init__(self, *args, **kwargs)

        # Setup physics
        self.og_position = pygame.Vector2(0,0)
        self.drift_acceleration = kwargs.get("drift_acceleration", 10)
        self.attack_acceleration = kwargs.get("attack_acceleration", 5)
        self.max_speed = kwargs.get("max_speed", 200)
        self.max_attack_speed = kwargs.get("max_attack_speed", 500)
        self.attack_position = pygame.Vector2(0,0)
        self.velocity = pygame.Vector2(0, 0)

        # Setup colliders
        self.collider_offset = kwargs.get("collider_offset", pygame.Vector2(0,0))
        self.collider_size = kwargs.get("collider_size", pygame.Vector2(0,0))
        self.collider = pygame.Rect(
            self.position.x+self.collider_offset.x, 
            self.position.y+self.collider_offset.y, 
            self.collider_size.x, 
            self.collider_size.y
        )

        # Setup state
        self.max_drift_distance = kwargs.get("max_drift_distance", 10)
        self.alert_distance = kwargs.get("alert_distance", 100)
        self.state = "idle"

        if "spritesheet_json_filename" in kwargs:
            self.play_animation("fly", loop=True)

    def render_colliders(self, surface, offset):
        """Draw current enemy collider to level space for debuging.
        Returns list of dirty rects which have been rendered to.

        Args:
            surface (pygame.Surface): Surface to render to
            offset (pygame.Vector2): Camera offset
        """
        dirty_rects = []

        collider = self.collider.move(offset)
        pygame.draw.rect(surface, (0,255,0), collider)
        dirty_rects.append(collider)

        return dirty_rects

    def update_state(self, player_position=None, state=None):
        """ Update enemy state and animations based on player_position

        Args:
            player_position (pygame.Vector2): Position of player in level space.
            state (str): Directly set state, if given no other state changes are enacted
        """
        if not state is None:
            self.state = state
        elif not (self.state == "death" or self.state == "dead"):
            # If player within range update state machine
            if (pygame.Vector2(self.collider.center) - player_position).length() < self.alert_distance:
                self.state = "alert"
                self.attack_position = player_position
            else:
                self.state = "idle"
                # When returning to idle reset og position
                self.og_position = self.position

    def physics_process(self, delta, colliders = None, player_position=None, attack_colliders=None):
        """ Handles physics, animations and updates state for flying enemy.

        Args:
            delta (float): Constant physics tick, eg. 1 / fps (required).
            colliders ([pygame.Rect]): List of rectangles describing the levels physical colliders. 
            player_position (pygame.Vector2): Level space position of player used to face enemy towards player.
            attack_colliders ([pygame.Rect]): List of rectangles which will damage an enemy, eg. list of player attack colliders. 
        """
        is_damaged = False

        # Face direction of velocity
        self.flipX = self.velocity.x < 0

        # Handle updating velocity when not dying
        if not (self.state == "death" or self.state == "dead"):
            if self.state == "alert":
                # Still add random velocity when attacking to have very rudimentary path finding and increase likelyhood of missing player
                rand_vel_x = random.uniform(-self.drift_acceleration, self.drift_acceleration)
                rand_vel_y = random.uniform(-self.drift_acceleration, self.drift_acceleration)
                self.velocity += pygame.Vector2(rand_vel_x, rand_vel_y)
                
                # Get direction vector to player and accelerate towards it
                if (self.attack_position - pygame.Vector2(self.collider.center)).length() > 0:
                    self.velocity += pygame.Vector2(self.attack_position - pygame.Vector2(self.collider.center)).normalize() * self.attack_acceleration

                # Limit velocity to max speed
                if self.velocity.length() > self.max_attack_speed:
                    self.velocity = self.velocity.scale_to_length(self.max_attack_speed)
            else:
                # Add random velocity
                self.velocity += pygame.Vector2(
                    random.uniform(-self.drift_acceleration, self.drift_acceleration), 
                    random.uniform(-self.drift_acceleration, self.drift_acceleration)
                )

                # If move beyond max drift distance reflect velocity off of tangent
                if (self.position - self.og_position).length() >= self.max_drift_distance:
                    self.velocity.reflect_ip(self.position - self.og_position)
                    self.velocity /= 2

                # Limit velocity to max speed
                if self.velocity.length() > self.max_speed:
                    self.velocity = self.velocity.normalize()*self.max_speed

            # Apply velocities using dx = v * dt
            self.position += self.velocity * delta

            # Move collider to new position
            self.collider.topleft = (self.position + self.collider_offset).xy

            # Check for damage events
            is_damaged = False
            if not attack_colliders == None:
                generous_collider = self.collider.inflate(1.2,1.2)
                collision = generous_collider.collidelist(attack_colliders)
                if not collision == -1:
                    # Kill enemy if damaged by setting state to dead
                    self.play_animation("death", 
                        on_animation_end=lambda self: self.update_state(state="dead"), 
                        on_animation_interrupt=lambda self: self.update_state(state="dead")
                    )
                    # Set into transition state while death animation playing and set flag
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

                        # Choose smaller transformation and reflect about surface if collision occurs, losing some velocity
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
        """ Returns a list of pygame.Rects which represent the enemies attack hitboxes """
        # Has no attacks so just return collider if not dying
        if not (self.state == "death" or self.state == "dead"):
            return [self.collider]
        return []
    
    # https://stackoverflow.com/questions/57225611/how-to-deepcopy-object-which-contains-pygame-surface
    def copy(self):
        """ Standard copy constructor for complex objects """
        copyobj = FlyingEnemy()
        for name, attr in self.__dict__.items():
            if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
                copyobj.__dict__[name] = attr.copy()
            else:
                copyobj.__dict__[name] = copy.deepcopy(attr)
        return copyobj

class ChallengeCollectable(Sprite.AnimatedSprite):
    """ Manages floating sprite which is collectable by player. Inherits from Sprite.AnimatedSprite. 
    
    Args:
        position (pygame.Vector2): level space position of sprite.
        spritesheet_json_filename (Str): string path of json for animation.
        spritesheet_scale (tuple): x, y to scale spritesheet resolution by.
        collider_offset (pygame.Vector2): x, y components of offset between collider and sprite.
        collider_size (pygame.Vector2): x, y components of size of collider.
        float_period (float): Number representing the period of sinusodial floating motion (not scaled by Pi).
        max_float_distance (float): Amplitude of sinusodial floating motion.
    """
    def __init__(self, *args, **kwargs):
        kwargs["calculate_flip"] = False
        kwargs["calculate_white"] = False
        Sprite.AnimatedSprite.__init__(self, *args, **kwargs)

        # Setup colliders
        self.collider_offset = kwargs.get("collider_offset", pygame.Vector2(0,0))
        self.collider_size = kwargs.get("collider_size", pygame.Vector2(0,0))
        self.collider = pygame.Rect(
            self.position.x+self.collider_offset.x, 
            self.position.y+self.collider_offset.y, 
            self.collider_size.x, 
            self.collider_size.y
        )

        # Setup state and physics
        self.og_position = kwargs.get("position", pygame.Vector2(0,0))
        self.float_period = kwargs.get("float_period", 2)
        self.max_float_distance = kwargs.get("max_float_distance", 10)
        self.float_time = 0
        self.state = "loop"

        if "spritesheet_json_filename" in kwargs:
            self.play_animation("loop", loop=True)

    def render_colliders(self, surface, offset):
        """Draw collider which causes player to collect collectable.
        Returns list of dirty rects which have been rendered to.

        Args:
            surface (pygame.Surface): Surface to render to
            offset (pygame.Vector2): Camera offset
        """
        dirty_rects = []

        collider = self.collider.move(offset)
        pygame.draw.rect(surface, (0,255,120), collider)
        dirty_rects.append(collider)

        return dirty_rects
    def update_state(self, state=None):
        """ Setter function for state

        Args:
            state (str): Value to set state to
        """
        if not state is None:
            self.state = state
    def physics_process(self, delta, player_collider=None):
        """ Handles floating motion and player collection for collectable.
        Returns True if it has been collected.

        Args:
            delta (float): Constant physics tick, eg. 1 / fps (required).
            player_collider (pygame.Rect): Rectangle representing level space collider of player.
        """
        if not (self.state == "death" or self.state == "dead"):
            self.float_time += delta

            # Apply simple harmonic motion to vertical position
            self.position = self.og_position + pygame.Vector2(0, self.max_float_distance) * math.sin(self.float_time / self.float_period)

            # Move collider to new position
            self.collider.topleft = (self.position + self.collider_offset).xy

            # Check for collection trigger by colliding player and self
            if not player_collider == None:
                if self.collider.colliderect(player_collider):
                    self.play_animation("death", 
                        on_animation_end=lambda self: self.update_state(state="dead"), 
                        on_animation_interrupt=lambda self: self.update_state(state="dead")
                    )
                    self.state = "death"
        return self.state == "dead"
                    
    # https://stackoverflow.com/questions/57225611/how-to-deepcopy-object-which-contains-pygame-surface
    def copy(self):
        """ Standard copy constructor for complex objects """
        copyobj = ChallengeCollectable()
        for name, attr in self.__dict__.items():
            if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
                copyobj.__dict__[name] = attr.copy()
            else:
                copyobj.__dict__[name] = copy.deepcopy(attr)

        return copyobj