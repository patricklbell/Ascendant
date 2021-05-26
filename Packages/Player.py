# Import standard libraries
import pygame
import copy
import random

# Import custom packages, access objects in Settings global space
from Packages import Settings, Sprite


class Player(Sprite.AnimatedSprite):
    """ Player class handling physics, rendering, and state. Inherits from Sprite.AnimatedSprite.

    Args:
        position (pygame.Vector2): level space position of sprite.
        spritesheet_json_filename (Str): string path of json for animation.
        spritesheet_scale (tuple): x, y to scale spritesheet resolution by.
        gravity (pygame.Vector2): x, y components of constant acceleration.
        air resistance (float): Factor to adjust friction force when player is in the air.
        floor resistance (float): Factor to adjust friction force when player is on the floor.
        water resistance (float): Factor to adjust friction force when player is in water.
        walk_speed (float): Constant walk speed independant of friction.
        water_walk_speed (float): Constant walk speed independant of friction when in water.
        jump_speed (float): Velocity added to y velocity at jump instant.
        jump_add_speed (float): Velocity added to y velocity while jump is held.
        jump_grace_frames (int): Number of frames after leaving ground where jump is still allowed.
        knockback_speed (pygame.Vector2): x, y components of speed added for player attacks against enemies. split on attack type.
        bounce_speed (pygame.Vector2): x, y components of speed added for player attacks against hitable_colliders. split on attack type.
        damage_knockback_speed (float): speed added to velocity during damage event, directed away from enemy.
        collider_offset (pygame.Vector2): x, y components of offset between collider and sprite.
        collider_size (pygame.Vector2): x, y components of size of collider.
        attack0_length (float): x component of side slash, added to player collider to get damage collider.
        attack0_width (float): y component of side slash, added to player collider to get damage collider.
        attack1_length (float): y component of down slash, added to player collider to get damage collider.
        attack1_width (float): x component of down slash, added to player collider to get damage collider.
        attack2_length (float): y component of up slash, added to player collider to get damage collider.
        attack2_width (float): x component of up slash, added to player collider to get damage collider.
        hearts (int): Number of health points player starts with, lost with damage or death_collider.
        iframes (int): Number of frames of invincibility after being damaged.
        transition_frames (int): Number of frames transition lasts.
        water_splash_json_filename (str): string path of json for splash animation.
        water_big_splash_json_filename (str): string path of json for bigger splash animation.
        short_stop_json_filename (str): string path of json for small dust cloud animation.
        hard_stop_json_filename (str): string path of json for large dust cloud animation.
    """

    def __init__(self, *args, **kwargs):
        # Inherit from AnimatedSprite for player animations
        kwargs["calculate_flip"] = True
        kwargs["calculate_white"] = True
        Sprite.AnimatedSprite.__init__(self, *args, **kwargs)

        # Setup physics and constants
        self.gravity = kwargs.get("gravity", pygame.Vector2(0, 500))
        self.air_resistance = kwargs.get("air_resistance", 1)
        self.floor_resistance = kwargs.get("floor_resistance", 10)
        self.water_resistance = kwargs.get("water_resistance", 9)
        self.walk_speed = kwargs.get("walk_speed", 200)
        self.water_walk_speed = kwargs.get("water_walk_speed", 100)
        self.knockback_speed = kwargs.get("knockback_speed", pygame.Vector2(200, 500))
        self.bounce_speed = kwargs.get("bounce_speed", pygame.Vector2(600, 500))
        self.damage_knockback_speed = kwargs.get("damage_knockback_speed", 10)
        self.jump_speed = kwargs.get("jump_speed", -200)
        self.jump_add_speed = kwargs.get("jump_add_speed", -500)
        self.jump_add_max_time = kwargs.get("jump_add_max_time", 1)
        self.jump_grace_max_frames = kwargs.get("jump_grace_frames", 5)
        self.jump_add_time = 0
        self.jumping = False
        self.jump_grace_frames = 0
        self.velocity = pygame.Vector2(0, 0)
        self.constant_velocity = pygame.Vector2(0, 0)

        # Setup player and attack collision info 
        self.collider_offset = kwargs.get("collider_offset", pygame.Vector2(0, 0))
        self.collider_size = kwargs.get("collider_size", pygame.Vector2(0, 0))
        self.attack0_length = kwargs.get("attack0_length", 100)
        self.attack0_width = kwargs.get("attack0_width", 50)
        self.attack1_length = kwargs.get("attack1_length", 100)
        self.attack1_width = kwargs.get("attack1_width", 50)
        self.attack2_length = kwargs.get("attack2_length", 100)
        self.attack2_width = kwargs.get("attack2_width", 50)
        
        # Create colliders true from parameters
        self.collider = pygame.Rect(
            self.position.x+self.collider_offset.x,
            self.position.y+self.collider_offset.y,
            self.collider_size.x,
            self.collider_size.y
        )
        # Collider to check if player is on the ground
        # Reduce size to correct for error, avoiding wall climb
        self.floor_collider = pygame.Rect(
            self.position.x+self.collider_offset.x+int(self.collider_size.x/1.6) / 4,
            self.position.y+self.collider_offset.y+(self.collider_size.y-1),
            self.collider_size.x/1.6,
            1
        )

        # Other properties
        self.hearts = kwargs.get("hearts", 3)
        self.iframe_length = kwargs.get("iframes", 120)
        self.transition_max_frames = kwargs.get("transition_frames", 100)
        self.transition_frames = 0
        self.transition = None

        # Load auxiliary animation
        self.water_splash_json_filename = kwargs.get(
            "water_splash_json_filename", None)
        if not self.water_splash_json_filename == None:
            self.water_splash = Sprite.AnimatedSprite(
                spritesheet_json_filename=self.water_splash_json_filename, spritesheet_scale=(0.5, 0.5))
        self.water_big_splash_json_filename = kwargs.get(
            "water_big_splash_json_filename", None)
        if not self.water_big_splash_json_filename == None:
            self.water_big_splash = Sprite.AnimatedSprite(
                spritesheet_json_filename=self.water_big_splash_json_filename, spritesheet_scale=(0.5, 0.5))
        self.short_stop_json_filename = kwargs.get(
            "short_stop_json_filename", None)
        if not self.short_stop_json_filename == None:
            self.short_stop = Sprite.AnimatedSprite(
                spritesheet_json_filename=self.short_stop_json_filename, calculate_flip=True, spritesheet_scale=(0.5, 0.5))
        self.hard_stop_json_filename = kwargs.get(
            "hard_stop_json_filename", None)
        if not self.hard_stop_json_filename == None:
            # Create two animations to allow double dust cloud
            self.hard_stop = Sprite.AnimatedSprite(
                spritesheet_json_filename=self.hard_stop_json_filename, calculate_flip=True, spritesheet_scale=(0.5, 0.5))
            self.hard_stop1 = Sprite.AnimatedSprite(
                spritesheet_json_filename=self.hard_stop_json_filename, calculate_flip=True, spritesheet_scale=(0.5, 0.5))
            self.hard_stop1.flipX = True

        # Setup state
        self.is_on_ground = False
        self.key_state = {"up": False, "down": False, "right": False,
                          "left": False, "jump": False, "attack": False}
        self.state = "idle"
        self.iframes = 0
        self.is_in_water = False
        self.can_save = False
        self.can_attack = True
        self.save_level = 0

        if "spritesheet_json_filename" in kwargs:
            self.play_animation("idle", loop=True)

    def get_attack_colliders(self):
        """ Returns all attack colliders at current animation frame. """
        if self.can_attack and self.animation_playing:
            # Adjust player colliders size and position to attack state
            if self.animation_name == "attack0" and self.frame_num >= 2:
                inflated = self.collider.inflate(
                    self.attack0_length, self.attack0_width)
                return [inflated.move((((not self.flipX)*2) - 1)*(self.attack0_length/2 + self.collider_size.x/2), 0)]

            if self.animation_name == "attack1" and self.frame_num >= 3 and self.frame_num <= 5:
                inflated = self.collider.inflate(
                    self.attack1_width, self.attack1_length)
                return [inflated.move(0, -self.attack1_length/2 - self.collider_size.y/2)]

            if self.animation_name == "attack2" and self.frame_num < 5:
                inflated = self.collider.inflate(
                    self.attack2_width, self.attack1_length)
                return [inflated.move(0, self.attack1_length/2 + self.collider_size.y/2)]

    def render_colliders(self, surface, offset):
        """ Draw current attack, player and floor colliders to level space for debuging.
        Returns list of dirty rects which have been rendered to.

        Args:
            surface (pygame.Surface): Surface to render to
            offset (pygame.Vector2): Camera offset
        """
        dirty_rects = []

        # Draw player and floor colliders to surface
        collider = self.collider.move(offset)
        pygame.draw.rect(surface, (0, 255, 0), collider)
        dirty_rects.append(collider)

        floor_collider = self.floor_collider.move(offset)
        pygame.draw.rect(surface, (255, 255, 0), floor_collider)
        dirty_rects.append(floor_collider)

        # Test conditions for valid attacks
        if self.can_attack:
            if self.animation_name == "attack0" and self.frame_num >= 2:
                # Create modified copy of player collider to resize into attack 
                attack_collider = collider.inflate(
                    self.attack0_length, self.attack0_width)
                attack_collider.move_ip(
                    (((not self.flipX)*2) - 1)*(self.attack0_length/2 + self.collider_size.x/2), 0)
                pygame.draw.rect(surface, (0, 0, 255), attack_collider)
                dirty_rects.append(attack_collider)

            if self.animation_name == "attack1" and self.frame_num >= 3 and self.frame_num <= 5:
                attack_collider = collider.inflate(
                    self.attack1_width, self.attack1_length)
                attack_collider.move_ip(
                    0, -self.attack1_length/2 - self.collider_size.y/2)
                pygame.draw.rect(surface, (0, 0, 255), attack_collider)
                dirty_rects.append(attack_collider)

            if self.animation_name == "attack2" and self.frame_num < 5:
                attack_collider = collider.inflate(
                    self.attack2_width, self.attack2_length)
                attack_collider.move_ip(
                    0, self.attack1_length/2 + self.collider_size.y/2)
                pygame.draw.rect(surface, (0, 0, 255), attack_collider)
                dirty_rects.append(attack_collider)
        return dirty_rects

    def physics_process(self, delta, colliders=None, damage_colliders=None, hitable_colliders=None, death_colliders=None, save_colliders=None, water_colliders=None, transitions=None, hit_occured=False, allow_movement=True):
        """ Calculates physics, state changes and transitions for player.
        Returns dictionary of state changes: {"reset": (bool), "transition": (dict or None), "respawn": (bool), "hit": (bool)}

        Args:
            delta (float): Constant physics tick, eg. 1 / fps.
            colliders ([pygame.rect]): List of level's physical colliders.
            damage_colliders ([pygame.rect]): List of level's damage colliders.
            hitable_colliders ([pygame.rect]): List of level's hitable colliders, bouncable objects.
            death_colliders ([pygame.rect]): List of level's death colliders, cause reset when collided.
            save_colliders ([pygame.rect]): List of level's save colliders, allow saving when colliding.
            water_colliders ([pygame.rect]): List of level's water colliders.
            transitions (dict): List of level's transition colliders, change levels when collided.
            hit_occured (bool): Flag for when any enemy attack was successful
            allow_movement (bool): Flag to allow player controled movement
        """
        # Setup returned state changes
        level_state_changes = {
            "reset": False, "transition": None, "respawn": False, "hit": False}

        # Setup dust states
        hard_landing, soft_landing, hard_turn = False, False, False

        # Check for transition events
        if not transitions == None and self.transition_frames == 0:
            # Extract colliders from transitions then calculate collision with player
            collision = self.collider.collidelist(
                [d["collider"] for d in transitions])
            
            # If collision occurs setup constant velocity based on direction 
            # Setup state to transition out of level 
            if not collision == -1:
                self.transition = transitions[collision]
                self.transition_frames = self.transition_max_frames
                if self.transition["direction"] == "S":
                    self.velocity.x = 0
                    self.velocity.y = abs(self.velocity.y)
                    Settings.SOUND_EFFECTS["jump"].Play(fade_in_ms=200)
                    self.play_animation("idle")
                elif self.transition["direction"] == "N":
                    self.velocity.x = 0
                    # Make sure player makes it out of the screen by having a mininum upwards velocity
                    self.velocity.y = -max(abs(self.velocity.y), self.gravity.y/5)
                    Settings.SOUND_EFFECTS["falling"].Play(fade_in_ms=200)
                    self.play_animation("idle")
                elif self.transition["direction"] == "W":
                    self.constant_velocity = pygame.Vector2(
                        -self.walk_speed, 0)
                    self.play_animation("walk")
                    Settings.SOUND_EFFECTS["run"].Play(fade_in_ms=200)
                elif self.transition["direction"] == "E":
                    self.constant_velocity = pygame.Vector2(self.walk_speed, 0)
                    Settings.SOUND_EFFECTS["run"].Play(fade_in_ms=200)
                    self.play_animation("walk")

        # During transitions don't allow player controlled movement and limited physics 
        if self.transition_frames > 0:
            self.transition_frames -= 1
            # When transition is complete change level_state_changes
            if self.transition_frames == 0:
                level_state_changes["transition"] = self.transition
            if not self.transition == None:
                # Apply gravity during horizontal transition, combats if player jumps into transition
                if not (self.transition["direction"] == "N" or self.transition["direction"] == "S"):
                    # Apply constant gravitational acceleration using dv = a * dt
                    self.velocity += delta * self.gravity
        else:
            if self.jump_grace_frames > 0:
                self.jump_grace_frames -= 1

            # Calculate physics with water and splash animations 
            if not water_colliders == None:
                collisions = self.collider.collidelist(water_colliders)
                if not collisions == -1:
                    collision = water_colliders[collisions]
                    if not self.is_in_water:
                        # If player just entered water make big splash
                        self.water_big_splash.play_animation("loop")
                        water_rect = self.water_big_splash.animations_data[self.water_big_splash.animation_index]["frames"][0].get_rect(
                        )
                        self.water_big_splash.position = pygame.Vector2(
                            self.position.x + self.collider_offset.x +
                            self.collider_size.x / 2 - water_rect.width / 2,
                            collision.top - water_rect.height,
                        )
                    else:
                        # If player walking in water make small splashes
                        if not self.water_splash.animation_playing and abs(self.constant_velocity.x) > 0:
                            self.water_splash.play_animation("loop")
                            water_rect = self.water_big_splash.animations_data[self.water_splash.animation_index]["frames"][0].get_rect(
                            )
                            self.water_splash.position = pygame.Vector2(
                                self.position.x + self.collider_offset.x +
                                self.collider_size.x / 2 - water_rect.width / 2,
                                collision.top - water_rect.height,
                            )
                    self.is_in_water = True
                else:
                    self.is_in_water = False
            else:
                self.is_in_water = False

            # Calculate damage events
            attack_colliders = self.get_attack_colliders()
            collision = False
            if not attack_colliders == None:
                for attack in attack_colliders:
                    collision = collision or (
                        not attack.collidelist(hitable_colliders) == -1)

            if hit_occured or collision:
                self.can_attack = False
                if collision:
                    # Impart velocity if player bounced of hitable collider
                    if self.animation_name == "attack0":
                        # Flip bounce depending on directions
                        self.velocity.x = (self.flipX*2 - 1) * \
                            self.bounce_speed.x
                        self.velocity.y = -self.bounce_speed.y/2
                    elif self.animation_name == "attack1" and not self.is_on_ground:
                        self.velocity.y = self.bounce_speed.y
                    elif self.animation_name == "attack2":
                        self.velocity.y = -self.bounce_speed.y
                # Ensure no double velocity, assumes bounce speed is greater
                elif hit_occured:
                    if self.animation_name == "attack0":
                        # Flip bounce depending on direction facing
                        self.velocity.x = (self.flipX*2 - 1) * \
                            self.knockback_speed.x
                    elif self.animation_name == "attack1" and not self.is_on_ground:
                        self.velocity.y = self.knockback_speed.y
                    elif self.animation_name == "attack2":
                        self.velocity.y = -self.knockback_speed.y

            # Handle damage flash and invincibility frames
            self.is_white = False
            if not self.iframes == 0 and not self.animation_name == "death":
                self.iframes -= 1

                # Map iframe completion to a flash distribution so player flashes less when losing invincibility
                flash_distribution = [1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0]
                if flash_distribution[int(((self.iframe_length - self.iframes) / self.iframe_length)*(len(flash_distribution)-1))]:
                    self.is_white = True

            # Handle player movement and animations
            if (not (self.animation_name == "sit" or self.animation_name == "unsit" or self.animation_name == "death") or (self.animation_finished and not self.animation_name == "sit")) and allow_movement:
                # Stay still if both keys are pressed
                if not self.key_state["left"] == self.key_state["right"]:
                    if self.key_state["right"]:
                        self.flipX = False

                        # If velocity changed instananeously show hard turn dust
                        if self.constant_velocity.x < 0:
                            hard_turn = True

                        if self.is_in_water:
                            self.constant_velocity.x = self.water_walk_speed
                        else:
                            self.constant_velocity.x = self.walk_speed

                        # Give walk animation low priority
                        if self.animation_name == "idle" or not self.animation_playing:
                            self.play_animation("walk", loop=True)
                    elif self.key_state["left"]:
                        self.flipX = True

                        # If velocity changed instananeously causes hard turn
                        if self.constant_velocity.x > 0:
                            hard_turn = True

                        if self.is_in_water:
                            self.constant_velocity.x = -self.water_walk_speed
                        else:
                            self.constant_velocity.x = -self.walk_speed

                        # Give walk animation low priority
                        if self.animation_name == "idle" or not self.animation_playing:
                            self.play_animation("walk", loop=True)
                else:
                    self.constant_velocity.x = 0
                    # Cancel walk animation to idle if player is still
                    if self.animation_name == "walk" or not self.animation_playing:
                        self.play_animation("idle", loop=True)
            else:
                self.constant_velocity.x = 0
                # Cancel walk animation to idle if player is still
                if (not allow_movement) and (self.animation_name == "walk" or not self.animation_playing):
                    self.play_animation("idle", loop=True)

            # Apply resistance forces and gravity
            if not self.velocity == pygame.Vector2(0, 0):
                if self.is_in_water:
                    self.velocity -= self.velocity * delta * self.water_resistance
                    self.velocity.y -= delta * \
                        random.randrange(0, self.gravity.y*1.5*100) / 100
                elif self.is_on_ground:
                    self.velocity -= self.velocity * delta * self.floor_resistance
                else:
                    self.velocity -= self.velocity * delta * self.air_resistance
            
            # Apply constant gravitational acceleration using dv = a * dt
            self.velocity += delta * self.gravity

            # Handle held jump velocity
            if (self.jumping and not self.key_state["jump"]) or self.jump_add_time > self.jump_add_max_time:
                self.jumping = False

            # Add extra velocity while jump is held
            if self.jumping:
                self.jump_add_time += delta
                self.velocity.y += delta * self.jump_add_speed
        old_position = copy.deepcopy(self.position)
        # Apply velocities using dx = v * dt
        self.position += (self.velocity + self.constant_velocity) * delta

        # Adjust collider positions after position change
        self.collider.x = self.position.x + self.collider_offset.x
        self.collider.y = self.position.y + self.collider_offset.y
        self.floor_collider.x = self.position.x + \
            self.collider_offset.x + int(self.collider_size.x/1.6) / 4
        self.floor_collider.y = self.position.y + \
            self.collider_offset.y + self.collider_size.y

        # Handle floor collider to determine if player is on the ground
        if not colliders == None:
            collision = self.floor_collider.collidelist(colliders)
            if not collision == -1:
                # If is_on_ground state changes player is landing
                if self.is_on_ground == False:
                    # Determine landing hardness from vertical velocity
                    if self.velocity.y > 200:
                        hard_landing = True
                    elif self.velocity.y > 10:
                        soft_landing = True

                self.is_on_ground = True

                # give extra frames after leaving edge where player can still jump
                self.jump_grace_frames = self.jump_grace_max_frames
            else:
                # No collisions mean players isnt on a floor
                self.is_on_ground = False

            # Handle perfectly inelastic collision between player and environment 
            for collider in colliders:
                if self.collider.colliderect(collider):
                    # Mininmise magnitude of translations so player is pushed out how they came by minimising absoluted value
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

                    # Combat high velocities passing through thin colliders
                    # NOTE: fails when v*dt > size since no collision occurs
                    if abs(self.velocity.x*delta) > self.collider.width / 2:
                        # Rather than minimising translation push player out in opposite direction to velocity 
                        if self.velocity.x > 0:
                            push_x = collider.left - self.collider.width - \
                                self.collider_offset.x - self.position.x
                        else:
                            push_x = collider.right - self.collider_offset.x - self.position.x

                    if abs(self.velocity.y*delta) > self.collider.height / 2:
                        # Rather than minimising translation push player out in opposite direction to velocity 
                        if self.velocity.y > 0:
                            push_y = collider.top - self.collider.height - \
                                self.collider_offset.y - self.position.y+1
                        else:
                            push_y = collider.bottom - self.collider_offset.y - self.position.y

                    # Choose smaller transformation between vertical and horizontal
                    if abs(push_x) < abs(push_y):
                        self.position.x = push_x + self.position.x
                        # Apply inelastic collision meaning all momentum is lost in direction of collision
                        if push_x > 0 and self.velocity.x < 0:
                            self.velocity.x = 0
                        elif push_x < 0 and self.velocity.x > 0:
                            self.velocity.x = 0
                    else:
                        self.position.y = push_y + self.position.y
                        # Apply inelastic collision meaning all momentum is lost in direction of collision
                        if push_y > 0 and self.velocity.y < 0:
                            self.velocity.y = 0
                        elif push_y < 0 and self.velocity.y > 0:
                            self.velocity.y = 0
        else:
            # If no colliders exist player cant be on ground
            self.is_on_ground = False

        # Check for damage events if not invincible or dying (otherwise continual damage would be applied)
        if not damage_colliders == None and self.iframes == 0 and not self.animation_name == "death":
            collision = self.collider.collidelist(damage_colliders)
            if not collision == -1:
                # Apply changes to state and animations
                level_state_changes["hit"] = True
                self.iframes = self.iframe_length
                self.play_animation("damage")
                self.hearts -= 1

                # Get vector between center of damage collider and center of player
                # NOTE: fails partially when player inside long collider
                s = pygame.Vector2(
                    damage_colliders[collision].left +
                    damage_colliders[collision].width/2,
                    damage_colliders[collision].top +
                    damage_colliders[collision].height/2,
                ) - (self.position + self.collider_offset + self.collider_size/2)

                # Apply knockback along axis if vector exists along axis
                self.velocity.x = self.velocity.x + \
                    self.damage_knockback_speed*(int(s.x < 0)*2 - 1)
                self.velocity.y = self.velocity.y + \
                    self.damage_knockback_speed*(int(s.y < 0)*2 - 1)

        # Check for death events if player is alive
        if not death_colliders == None and not self.animation_name == "death":
            collision = self.collider.collidelist(death_colliders)
            if not collision == -1:
                # Reset level if environmental death occurs
                self.hearts -= 1
                level_state_changes["reset"] = True

        # Respawn from last save if no lives are left if player is alive
        if self.hearts == 0 and not self.animation_name == "death":
            level_state_changes["respawn"] = True

        # Handle save colliders
        self.can_save = False
        if not save_colliders == None:
            # Set flag if player is in save collider
            self.can_save = not (self.collider.collidelist(save_colliders) == -1)

        # Create dust trails if moving on ground 
        if self.is_on_ground and abs((self.position - old_position).x) > 1:
            # Setup normal small dust trails if no hard turn and not already playing
            if not hard_turn and not self.short_stop.animation_playing:
                self.short_stop.play_animation("loop")

                # Get size of animation by getting first frames rectangle
                stop_rect = self.short_stop.animations_data[self.short_stop.animation_index]["frames"][0].get_rect()

                # Position and flip animations based on player position ensuring dust is behind
                self.short_stop.flipX = self.flipX
                if self.flipX:
                    self.short_stop.position = pygame.Vector2(
                        self.position.x + self.collider_size.x +
                        self.collider_offset.x - stop_rect.width,
                        self.position.y + self.collider_offset.y +
                        self.collider_size.y - stop_rect.height,
                    )
                else:
                    self.short_stop.position = pygame.Vector2(
                        self.position.x + self.collider_offset.x,
                        self.position.y + self.collider_offset.y +
                        self.collider_size.y - stop_rect.height,
                    )
            # Similarly setup hard turn animation if not already playing
            elif hard_turn and not self.hard_stop.animation_playing:
                self.hard_stop.play_animation("loop")
                stop_rect = self.hard_stop.animations_data[self.hard_stop.animation_index]["frames"][0].get_rect()

                self.hard_stop.flipX = self.flipX
                if self.flipX:
                    self.hard_stop.position = pygame.Vector2(
                        self.position.x + self.collider_size.x +
                        self.collider_offset.x - stop_rect.width,
                        self.position.y + self.collider_offset.y +
                        self.collider_size.y - stop_rect.height,
                    )
                else:
                    self.hard_stop.position = pygame.Vector2(
                        self.position.x + self.collider_offset.x,
                        self.position.y + self.collider_offset.y +
                        self.collider_size.y - stop_rect.height,
                    )

        # Handle landing dust animations
        if hard_landing and not self.hard_stop1.animation_playing:
            self.hard_stop.play_animation("loop")
            self.hard_stop1.play_animation("loop")
            # Assume animation are the same
            stop_rect = self.hard_stop.animations_data[self.hard_stop.animation_index]["frames"][0].get_rect()

            # Position clouds symmetrically spreading from landing
            self.hard_stop.flipX = False
            self.hard_stop.position = pygame.Vector2(
                self.position.x + self.collider_size.x +
                self.collider_offset.x - stop_rect.width,
                self.position.y + self.collider_offset.y +
                self.collider_size.y - stop_rect.height,
            )
            self.hard_stop1.position = pygame.Vector2(
                self.position.x + self.collider_offset.x,
                self.position.y + self.collider_offset.y +
                self.collider_size.y - stop_rect.height,
            )
        
        # Create sounds depending on player state, only outside transition to avoid strange audio
        if self.transition == None:
            # Fade in and out falling loop
            if self.velocity.y > 100 and not self.is_on_ground and not Settings.SOUND_EFFECTS["falling"].IsPlaying():
                # Play while player has sufficient downwards velocity
                Settings.SOUND_EFFECTS["falling"].Play(fade_in_ms=200)
            else:
                Settings.SOUND_EFFECTS["falling"].Stop(fade_out_ms=100)

            # Play and cancel walking or swiming loops depending on environment
            if abs(self.constant_velocity.x) > 0 and self.is_on_ground:
                if self.is_in_water:
                    # Cancel sound rather than fading, covered by splash sound
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

            # Play landing sounds
            if (hard_landing or soft_landing) and self.is_in_water:
                # Play splashing sounds when landing on bottom
                # NOTE: will fail for deep water since player wont land at same time as entering
                Settings.SOUND_EFFECTS["land_splash"].Play(fade_in_ms=100)
            elif hard_landing:
                Settings.SOUND_EFFECTS["land_hard"].Play(fade_in_ms=200)
            elif soft_landing:
                Settings.SOUND_EFFECTS["land_soft"].Play(fade_in_ms=200)

            # Play damage and death sounds
            if level_state_changes["hit"] or level_state_changes["reset"]:
                Settings.SOUND_EFFECTS["damage"].Play(fade_in_ms=200)
            if level_state_changes["respawn"] or level_state_changes["respawn"]:
                if not Settings.SOUND_EFFECTS["death"].IsPlaying():
                    Settings.SOUND_EFFECTS["death"].Play(fade_in_ms=200)

        return level_state_changes

    def update_animation(self, delta):
        """ Updates player, and dust and splash animations. Called by render if delta is given

        Args:
            delta (float): delta time between last call 

        """
        # Update base and auxiliary animations
        super().update_animation(delta)

        self.water_big_splash.update_animation(delta)
        self.water_splash.update_animation(delta)

        self.short_stop.update_animation(delta)
        self.hard_stop.update_animation(delta)
        self.hard_stop1.update_animation(delta)

    def render(self, surface, offset=pygame.Vector2(0, 0), size=None, delta=None):
        """ renders player, and splash and splashes to surface.
        
        Args:
            surface (pygame.Surface): level space surface to render to (required).
            offset (pygame.Vector2): camera position which offsets all rendering.
            size (None): polymorphic parameter which is ignored.
            delta (float): delta time since last update, updates animations.
        """
        # Update if delta given
        if not delta == None:
            self.update_animation(delta)
        
        # Render all sprites
        dirty_rects = super().render(surface, offset)

        dirty_rects += self.water_big_splash.render(surface, offset)
        dirty_rects += self.water_splash.render(surface, offset)

        dirty_rects += self.short_stop.render(surface, offset)
        dirty_rects += self.hard_stop.render(surface, offset)
        dirty_rects += self.hard_stop1.render(surface, offset)

        # Return rects to describe stale parts of screen
        return dirty_rects

    def input(self, events):
        """ Proccess pygame events for player actions.
        Returns if player triggered a save.

        Args:
            events ([pygame.event.Event]) list of pygame events.

        """
        save = False

        # setup local function to reallow attacks after an attack animation is completed
        def reenable_attack(self):
            self.can_attack = True

        for event in events:
            if event.type == pygame.KEYDOWN:
                # Mapping keydown bindings to actions and updating key states while button is pressed
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["up"]):
                    self.key_state["up"] = True

                    # During sitting up button causes player to unsit
                    if self.animation_name == "sit":
                        self.play_animation("unsit")
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["down"]):
                    self.key_state["down"] = True

                    # Down triggers save if player can
                    if self.can_save and (not self.animation_name == "death"):
                        # If player already sitting unsit when pressing down
                        if self.animation_name == "sit":
                            self.play_animation("unsit")
                        # Save game otherwise and ensure no velocity while sitting
                        else:
                            save = True
                            self.velocity = pygame.Vector2(0, 0)
                            self.constant_velocity = pygame.Vector2(0, 0)
                            self.play_animation("sit")
                    # If player can't save and is attacking allow a change to the type of attack
                    else:
                        # Allows late triggering of down slash
                        if self.animation_name == "attack0" and self.frame_num < 4 and not self.is_on_ground and (not self.animation_name == "death"):
                            Settings.SOUND_EFFECTS["attack"].Stop(
                                fade_out_ms=50)
                            Settings.SOUND_EFFECTS["big_attack"].Play(
                                fade_in_ms=50)
                            self.play_animation("attack2")
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["attack"]):
                    # If player sitting attack unsits
                    if self.animation_name == "sit":
                        self.play_animation("unsit")
                    else:
                        # Set state if valid since holding attack isnt meaningful
                        self.key_state["attack"] = True

                        # Trigger attack of correct type if valid
                        if not self.animation_name == "death":
                            # Allow down slash when pressing down and attacking in the air
                            if self.key_state["down"] and not self.is_on_ground:
                                if not (self.animation_name == "attack2" and self.animation_playing):
                                    self.play_animation(
                                        "attack2", on_animation_end=reenable_attack, on_animation_interrupt=reenable_attack)
                                    Settings.SOUND_EFFECTS["big_attack"].Play(
                                        fade_in_ms=200)
                            # Always allow up slash
                            elif self.key_state["up"]:
                                if not (self.animation_name == "attack1" and self.animation_playing):
                                    self.play_animation(
                                        "attack1", on_animation_end=reenable_attack, on_animation_interrupt=reenable_attack)
                                    Settings.SOUND_EFFECTS["big_attack"].Play(
                                        fade_in_ms=200)
                            # Default to normal attack
                            else:
                                if not (self.animation_name == "attack0" and self.animation_playing):
                                    self.play_animation(
                                        "attack0", on_animation_end=reenable_attack, on_animation_interrupt=reenable_attack)
                                    Settings.SOUND_EFFECTS["attack"].Play(
                                        fade_in_ms=200)
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["jump"]):
                    # Jump causes unsit
                    if self.animation_name == "sit":
                        self.play_animation("unsit")
                    else:
                        # Holding jump is only meaningful if intially valid
                        self.key_state["jump"] = True

                        # Cause jump if alive player either on the ground or has grace frames, disallow during transition
                        if (self.is_on_ground or self.jump_grace_frames > 0) and not (self.transition_frames > 0) and (not self.animation_name == "death"):
                            self.jumping = True

                            # Reset jump add time so extra velocity can be added while button is held
                            self.jump_add_time = 0

                            # Dont interupt iframes with jump for visual reasons
                            if self.iframes == 0:
                                self.play_animation("jump")

                            # Add initial jump upwards speed
                            self.velocity.y += self.jump_speed

                            Settings.SOUND_EFFECTS["jump"].Play(fade_in_ms=100)
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["right"]):
                    # Movement causes unsit
                    if self.animation_name == "sit":
                        self.play_animation("unsit")

                    self.key_state["right"] = True
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["left"]):
                    # Movement causes unsit
                    if self.animation_name == "sit":
                        self.play_animation("unsit")

                    self.key_state["left"] = True
            if event.type == pygame.KEYUP:
                # Reset key state when button is released
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["jump"]):
                    self.key_state["jump"] = False
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["up"]):
                    self.key_state["up"] = False
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["down"]):
                    self.key_state["down"] = False
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["right"]):
                    self.key_state["right"] = False
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["left"]):
                    self.key_state["left"] = False
        return save

    def input_static(self, events):
        """ Handles pygame events for staticly player while paused so buttons can be held across pausing.

        Args:
            events ([pygame.event.Event]) list of pygame events.
        """
        for event in events:
            # Set key state to true when keydown and false when keyup for each binding
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["jump"]):
                    self.key_state["jump"] = True
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["up"]):
                    self.key_state["up"] = True
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["down"]):
                    self.key_state["down"] = True
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["right"]):
                    self.key_state["right"] = True
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["left"]):
                    self.key_state["left"] = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["jump"]):
                    self.key_state["jump"] = False
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["up"]):
                    self.key_state["up"] = False
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["down"]):
                    self.key_state["down"] = False
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["right"]):
                    self.key_state["right"] = False
                if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["left"]):
                    self.key_state["left"] = False

    # https://stackoverflow.com/questions/57225611/how-to-deepcopy-object-which-contains-pygame-surface
    def copy(self):
        """ Standard copy constructor for complex objects """

        copyobj = Player()
        for name, attr in self.__dict__.items():
            if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
                copyobj.__dict__[name] = attr.copy()
            else:
                copyobj.__dict__[name] = copy.deepcopy(attr)
        return copyobj
