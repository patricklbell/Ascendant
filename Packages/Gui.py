import pygame
import pygame_gui
import json
from Packages import Settings, Sprite


class Gui():
    """ Manages displaying and handles events for all non dialog GUI. 
    
    Args:
        health_spritesheet_filename (str): File path for health animation (required).
        alternate_health_spritesheet_filename (str): File path for extra health animations (required).
        health_sprite_filename (str): File path for health image sprite (required).
        alternate_health_sprite_filename (str): File path for extra health image sprite (required).
        title_animation_filename (str): File path for title logo animation (required).
        title_background_filename (str): File path for title background animation (required).
        save_sprite_filename (str): File path for save hint image sprite (required).
        save_animation_filename (str): File path for save animation icon (required).
        state (str): Optional initial gui state.
    """

    def __init__(self, health_spritesheet_filename, alternate_health_spritesheet_filename, health_sprite_filename, alternate_health_sprite_filename, title_animation_filename, title_background_filename, save_sprite_filename, save_animation_filename, state=None):
        # Setup state
        self.to_bind_key = ""
        self.selected_save = 0

        # Setup animations and image sprites for title and ingame gui 
        scale = max(Settings.RESOLUTION[0] / 700, Settings.RESOLUTION[1] / 394)
        self.title_background = Sprite.AnimatedSprite(
            spritesheet_json_filename=title_background_filename, spritesheet_scale=(scale, scale))
        self.title_background.play_animation("loop", loop=True)

        self.title_animation = Sprite.AnimatedSprite(position=pygame.Vector2(
            Settings.RESOLUTION[0]/2-270/2, 75), spritesheet_json_filename=title_animation_filename, spritesheet_scale=(0.25, 0.25))
        self.title_animation.play_animation("loop", loop=True)

        self.health_bar = Sprite.AnimatedSprite(
            spritesheet_json_filename=health_spritesheet_filename, spritesheet_scale=(2, 2))
        self.health_bar.play_animation("idle", loop=True)
        self.alt_health_bar = Sprite.AnimatedSprite(
            spritesheet_json_filename=alternate_health_spritesheet_filename, spritesheet_scale=(2, 2))
        self.alt_health_bar.play_animation("idle", loop=True)

        self.health_outline = Sprite.ImageSprite(
            health_sprite_filename, scale=(2, 2))
        self.health_outline.z = 2
        self.health_outline_alt = Sprite.ImageSprite(
            alternate_health_sprite_filename, scale=(2, 2))
        self.health_outline_alt.z = 2

        self.save_sprite = Sprite.ImageSprite(
            save_sprite_filename, scale=(1, 1))
        self.save_animation = Sprite.AnimatedSprite(
            spritesheet_json_filename=save_animation_filename, position=pygame.Vector2(0, Settings.RESOLUTION[1]/2-32), spritesheet_scale=(0.5, 0.5))

        # Setup positioning constants
        vertical_gap, vertical_height = 40, 30

        # Read saves to setup labels and see which saves have begun
        save_labels = ["", "", ""]
        save_buttons = ["", "", ""]
        self.has_begun = [False, False, False]
        for i in range(3):
            save_filename = Settings.SAVE_FILETEMPLATE.substitute(num=str(i+1))
            try:
                with open(save_filename) as json_file:
                    json_data = json.load(json_file)
                self.has_begun[i] = json_data["has_begun"]
                # Subsitute into format string if save has been begun otherwise show new game button
                if json_data["has_begun"]:
                    save_labels[i] = f"SAVE {i+1} ({json_data['title_info']['percentage_completion']}%): {json_data['name'][:6] + (json_data['name'][6:] and '..')}"
                    save_buttons[i] = "COTINUE"
                else:
                    save_labels[i] = f"SAVE {i+1}"
                    save_buttons[i] = "NEW GAME"
            except FileNotFoundError as e:
                if Settings.DEBUG:
                    print(f"Failed to load save {save_filename}, error: ", e)
                # By default show new game since the save will be written if it doesnt exist
                save_labels[i] = f"SAVE {i+1}"
                save_buttons[i] = "NEW GAME"

        # Setup dictionary containing each menu's pygame_gui elements, positioning with relative rect
        self.menus = {
            "title": {
                "new_game": pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0] / 2+327/2-200, 160), (200, 50)),
                    text="PLAY",
                    manager=Settings.gui_manager,
                    starting_height=2,
                ),
                "settings": pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0] / 2+327/2-200, 200), (200, 50)),
                    text="SETTINGS",
                    manager=Settings.gui_manager,
                    starting_height=2,
                ),
                "quit": pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0] / 2+327/2-200, 240), (200, 50)),
                    text="QUIT",
                    manager=Settings.gui_manager,
                    starting_height=2,
                ),
            },
            "end_game": {
                "end_game_label": pygame_gui.elements.UILabel(
                    text=f"You have ascended",
                    object_id='#center_label',
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2-100, Settings.RESOLUTION[1]*0.5), (300, vertical_height)),
                    manager=Settings.gui_manager
                ),
                "challenge_label": pygame_gui.elements.UILabel(
                    text=f"Challenges: 0/3",
                    object_id='#center_label',
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2-100, Settings.RESOLUTION[1]*0.5 + vertical_height), (300, vertical_height)),
                    manager=Settings.gui_manager
                ),
                "quit": pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]-400-vertical_gap, Settings.RESOLUTION[1] - vertical_gap - vertical_height), (400, 50)),
                    text="RETURN TO MENU",
                    manager=Settings.gui_manager,
                    starting_height=2,
                ),
            },
            "select_save": {
                "save1_label": pygame_gui.elements.UILabel(
                    text=save_labels[0],
                    object_id='#small_label',
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2-220, Settings.RESOLUTION[1]/3), (220, vertical_height)),
                    manager=Settings.gui_manager
                ),
                "save1": pygame_gui.elements.UIButton(
                    text=save_buttons[0],
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2, Settings.RESOLUTION[1]/3), (200, vertical_height)),
                    object_id='#small_button',
                    manager=Settings.gui_manager,
                    starting_height=2,
                ),
                "save2_label": pygame_gui.elements.UILabel(
                    text=save_labels[1],
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2-220, Settings.RESOLUTION[1]/3+vertical_gap), (220, vertical_height)),
                    object_id='#small_label',
                    manager=Settings.gui_manager
                ),
                "save2": pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2, Settings.RESOLUTION[1]/3+vertical_gap), (200, vertical_height)),
                    text=save_buttons[1],
                    object_id='#small_button',
                    manager=Settings.gui_manager,
                    starting_height=2,
                ),
                "save3_label": pygame_gui.elements.UILabel(
                    text=save_labels[2],
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2-220, Settings.RESOLUTION[1]/3+vertical_gap*2), (220, vertical_height)),
                    object_id='#small_label',
                    manager=Settings.gui_manager,
                ),
                "save3": pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2, Settings.RESOLUTION[1]/3+vertical_gap*2), (200, vertical_height)),
                    text=save_buttons[2],
                    object_id='#small_button',
                    manager=Settings.gui_manager,
                    starting_height=2,
                ),
                "back": pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2-100, Settings.RESOLUTION[1]*8/9-25), (200, 50)),
                    text=" BACK",
                    # object_id='#center_button',
                    manager=Settings.gui_manager,
                    starting_height=2,
                ),
            },
            "name": {
                "title": pygame_gui.elements.UILabel(
                    text="Enter a name:",
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2 - 100, Settings.RESOLUTION[1]/2 - vertical_height*4), (200, vertical_height)),
                    object_id="#center_label",
                    manager=Settings.gui_manager,
                ),
                "entry": pygame_gui.elements.UITextEntryLine(
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2 - 100, Settings.RESOLUTION[1]/2 - vertical_height), (200, vertical_height)),
                    manager=Settings.gui_manager,
                ),
                "continue": pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2-130, Settings.RESOLUTION[1]*7/9-25), (200, 50)),
                    text="CONTINUE",
                    manager=Settings.gui_manager,
                    starting_height=2,
                ),
            },

            "paused": {
                "panel": pygame_gui.elements.UIPanel(relative_rect=pygame.Rect((0, 0), Settings.RESOLUTION), starting_layer_height=-1, manager=Settings.gui_manager),
                "resume": pygame_gui.elements.UIButton(starting_height=2, relative_rect=pygame.Rect((Settings.RESOLUTION[0]/2-50, Settings.RESOLUTION[1]/2-100), (200, 50)), text="RESUME", manager=Settings.gui_manager),
                "settings": pygame_gui.elements.UIButton(starting_height=2, relative_rect=pygame.Rect((Settings.RESOLUTION[0]/2-50, Settings.RESOLUTION[1]/2-40), (200, 50)), text="CONTROLS", manager=Settings.gui_manager),
                "quit": pygame_gui.elements.UIButton(starting_height=2, relative_rect=pygame.Rect((Settings.RESOLUTION[0]/2-50, Settings.RESOLUTION[1]/2+20), (200, 50)), text="TO TITLE", manager=Settings.gui_manager),
            },
            "settings": {
                "panel": pygame_gui.elements.UIPanel(relative_rect=pygame.Rect((0, 0), Settings.RESOLUTION), starting_layer_height=-2, manager=Settings.gui_manager),
                "title": pygame_gui.elements.UILabel(
                    text="CONTROLS",
                    object_id='#center_label',
                    relative_rect=pygame.Rect(
                        (0, Settings.RESOLUTION[1]/8), (Settings.RESOLUTION[0], vertical_height)),
                    manager=Settings.gui_manager
                ),
                "attack_label": pygame_gui.elements.UILabel(
                    text="ATTACK",
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2-250, Settings.RESOLUTION[1]/8+vertical_gap), (200, vertical_height)),
                    object_id='#small_label',
                    manager=Settings.gui_manager
                ),
                "attack": pygame_gui.elements.UIButton(starting_height=2,
                                                       relative_rect=pygame.Rect(
                                                           (Settings.RESOLUTION[0]/2+100, Settings.RESOLUTION[1]/8+vertical_gap), (100, vertical_height)),
                                                       text=Settings.USER_SETTINGS["bindings"]["attack"].upper(
                                                       ),
                                                       object_id='#small_button',
                                                       manager=Settings.gui_manager
                                                       ),
                "jump_label": pygame_gui.elements.UILabel(
                    text="JUMP",
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2-250, Settings.RESOLUTION[1]/8+vertical_gap*2), (200, vertical_height)),
                    object_id='#small_label',
                    manager=Settings.gui_manager
                ),
                "jump": pygame_gui.elements.UIButton(starting_height=2,
                                                     relative_rect=pygame.Rect(
                                                         (Settings.RESOLUTION[0]/2+100, Settings.RESOLUTION[1]/8+vertical_gap*2), (100, vertical_height)),
                                                     text=Settings.USER_SETTINGS["bindings"]["jump"].upper(
                                                     ),
                                                     object_id='#small_button',
                                                     manager=Settings.gui_manager
                                                     ),
                "left_label": pygame_gui.elements.UILabel(
                    text="LEFT",
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2-250, Settings.RESOLUTION[1]/8+vertical_gap*3), (200, vertical_height)),
                    object_id='#small_label',
                    manager=Settings.gui_manager
                ),
                "left": pygame_gui.elements.UIButton(starting_height=2,
                                                     relative_rect=pygame.Rect(
                                                         (Settings.RESOLUTION[0]/2+100, Settings.RESOLUTION[1]/8+vertical_gap*3), (100, vertical_height)),
                                                     text=Settings.USER_SETTINGS["bindings"]["left"].upper(
                                                     ),
                                                     object_id='#small_button',
                                                     manager=Settings.gui_manager
                                                     ),
                "right_label": pygame_gui.elements.UILabel(
                    text="RIGHT",
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2-250, Settings.RESOLUTION[1]/8+vertical_gap*4), (200, vertical_height)),
                    object_id='#small_label',
                    manager=Settings.gui_manager
                ),
                "right": pygame_gui.elements.UIButton(starting_height=2,
                                                      relative_rect=pygame.Rect(
                                                          (Settings.RESOLUTION[0]/2+100, Settings.RESOLUTION[1]/8+vertical_gap*4), (100, vertical_height)),
                                                      text=Settings.USER_SETTINGS["bindings"]["right"].upper(
                                                      ),
                                                      object_id='#small_button',
                                                      manager=Settings.gui_manager
                                                      ),
                "up_label": pygame_gui.elements.UILabel(
                    text="UP",
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2-250, Settings.RESOLUTION[1]/8+vertical_gap*5), (200, vertical_height)),
                    object_id='#small_label',
                    manager=Settings.gui_manager
                ),
                "up": pygame_gui.elements.UIButton(starting_height=2,
                                                   relative_rect=pygame.Rect(
                                                       (Settings.RESOLUTION[0]/2+100, Settings.RESOLUTION[1]/8+vertical_gap*5), (100, vertical_height)),
                                                   text=Settings.USER_SETTINGS["bindings"]["up"].upper(
                                                   ),
                                                   object_id='#small_button',
                                                   manager=Settings.gui_manager
                                                   ),
                "down_label": pygame_gui.elements.UILabel(
                    text="DOWN",
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2-250, Settings.RESOLUTION[1]/8+vertical_gap*6), (200, vertical_height)),
                    object_id='#small_label',
                    manager=Settings.gui_manager
                ),
                "down": pygame_gui.elements.UIButton(starting_height=2,
                                                     relative_rect=pygame.Rect(
                                                         (Settings.RESOLUTION[0]/2+100, Settings.RESOLUTION[1]/8+vertical_gap*6), (100, vertical_height)),
                                                     text=Settings.USER_SETTINGS["bindings"]["down"].upper(
                                                     ),
                                                     object_id='#small_button',
                                                     manager=Settings.gui_manager
                                                     ),
                "dialog_label": pygame_gui.elements.UILabel(
                    text="DIALOG",
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2-250, Settings.RESOLUTION[1]/8+vertical_gap*7), (200, vertical_height)),
                    object_id='#small_label',
                    manager=Settings.gui_manager
                ),
                "dialog": pygame_gui.elements.UIButton(starting_height=2,
                                                       relative_rect=pygame.Rect(
                                                           (Settings.RESOLUTION[0]/2+100, Settings.RESOLUTION[1]/8+vertical_gap*7), (100, vertical_height)),
                                                       text=Settings.USER_SETTINGS["bindings"]["dialog"].upper(
                                                       ),
                                                       object_id='#small_button',
                                                       manager=Settings.gui_manager
                                                       ),
                "save": pygame_gui.elements.UIButton(starting_height=2,
                                                     relative_rect=pygame.Rect(
                                                         (Settings.RESOLUTION[0]/2-170, Settings.RESOLUTION[1]*8/9-25), (200, 50)),
                                                     text="SAVE",
                                                     manager=Settings.gui_manager
                                                     ),
            },
            "title_settings": {
                "fullscreen_label": pygame_gui.elements.UILabel(
                    text="FULLSCREEN",
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2-200, Settings.RESOLUTION[1]/6), (200, vertical_height)),
                    object_id="#small_label",
                    manager=Settings.gui_manager
                ),
                "fullscreen": pygame_gui.elements.UIButton(starting_height=2,
                                                           relative_rect=pygame.Rect(
                                                               (Settings.RESOLUTION[0]/2+100, Settings.RESOLUTION[1]/6), (100, vertical_height)),
                                                           text=[
                                                               "OFF", "ON"][Settings.USER_SETTINGS["fullscreen"]],
                                                           object_id="#small_button",
                                                           manager=Settings.gui_manager,
                                                           ),
                "resolution_label": pygame_gui.elements.UILabel(
                    text="ASPECT RATIO",
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2-200, Settings.RESOLUTION[1]/6+vertical_gap), (200, vertical_height)),
                    object_id="#small_label",
                    manager=Settings.gui_manager
                ),
                "resolution": pygame_gui.elements.UIDropDownMenu(
                    options_list=["11:3", "21:9", "16:9", "16:10", "4:3"],
                    # Match current resolution to an aspect ratio
                    starting_option=["11:3", "21:9", "16:9", "16:10", "4:3"][[
                        "1100x300", "800x340", "770x430", "600x380", "660x500"].index(Settings.RESOLUTION_STR)],
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2, Settings.RESOLUTION[1]/6+vertical_gap), (140, vertical_height)),
                    manager=Settings.gui_manager,
                ),
                "music_label": pygame_gui.elements.UILabel(
                    text="MUSIC",
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2-200, Settings.RESOLUTION[1]/6+2*vertical_gap), (200, vertical_height)),
                    object_id="#small_label",
                    manager=Settings.gui_manager
                ),
                "music": pygame_gui.elements.UIButton(starting_height=2,
                                                      relative_rect=pygame.Rect(
                                                          (Settings.RESOLUTION[0]/2+100, Settings.RESOLUTION[1]/6+2*vertical_gap), (100, vertical_height)),
                                                      text=[
                                                          "OFF", "ON"][Settings.USER_SETTINGS["music"]],
                                                      object_id="#small_button",
                                                      manager=Settings.gui_manager,
                                                      ),
                "music_volume": pygame_gui.elements.UIHorizontalSlider(
                    start_value=Settings.USER_SETTINGS["music_volume"],
                    value_range=(0, 100),
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2+100, Settings.RESOLUTION[1]/6+3*vertical_gap), (100, vertical_height/2)),
                    manager=Settings.gui_manager,
                ),
                "sound_effects_label": pygame_gui.elements.UILabel(
                    text="SOUND EFFECTS",
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2-200, Settings.RESOLUTION[1]/6+4*vertical_gap), (200, vertical_height)),
                    object_id="#small_label",
                    manager=Settings.gui_manager
                ),
                "sound_effects": pygame_gui.elements.UIButton(starting_height=2,
                                                              relative_rect=pygame.Rect(
                                                                  (Settings.RESOLUTION[0]/2+100, Settings.RESOLUTION[1]/6+4*vertical_gap), (100, vertical_height)),
                                                              text=[
                                                                  "OFF", "ON"][Settings.USER_SETTINGS["sound_effects"]],
                                                              object_id="#small_button",
                                                              manager=Settings.gui_manager,
                                                              ),
                "sound_effects_volume": pygame_gui.elements.UIHorizontalSlider(
                    start_value=Settings.USER_SETTINGS["sound_effects_volume"],
                    value_range=(0, 100),
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2+100, Settings.RESOLUTION[1]/6+5*vertical_gap), (100, vertical_height/2)),
                    manager=Settings.gui_manager,
                ),
                "save": pygame_gui.elements.UIButton(starting_height=2,
                                                     relative_rect=pygame.Rect(
                                                         (Settings.RESOLUTION[0]/2-100, Settings.RESOLUTION[1]*8/9-25), (200, 50)),
                                                     text="SAVE",
                                                     manager=Settings.gui_manager
                                                     ),
            },
            "binding": {
                "panel": pygame_gui.elements.UIPanel(relative_rect=pygame.Rect((0, 0), Settings.RESOLUTION), starting_layer_height=1, manager=Settings.gui_manager),
                "key_label": pygame_gui.elements.UILabel(
                    text="Press Key",
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2-200, Settings.RESOLUTION[1]/2-25), (400, 50)),
                    manager=Settings.gui_manager
                ),
            }
        }
        self.set_state(state)

    def render_ingame(self, delta, surface, player, num_challenges, offset=pygame.Vector2(0, 0)):
        """ Draws ingame gui including health bar and save hint and logo animation.
        Returns list of dirty rectangles which have been rendered to.

        Args:
            delta (float): Delta time elapsed since last render call, used for animations.
            surface (pygame.Surface): Surface to be rendered to in gui space.
            player (Player.Player): Player object to determine state.
            num_challenges (int): Number of challenges player has completed.
            offset (pygame.Vector2): Optional offset between player and save hint
        """
        dirty_rects = []

        health_fraction = (player.hearts-1) / (Settings.PLAYER_HEARTS-1)
        if player.hearts == 0:
            health_fraction = 0

        # Crop health to cuttoff missing health
        if health_fraction == 0:
            # For last live show empty health bar
            health_crop = 0
        else:
            health_crop = 16 + int(42*health_fraction)
        self.health_bar.render(surface, (10, 10),
                               size=(0, 0, health_crop*2, 17*2), delta=delta)
        
        # Crop extra health by different amount to show each extra life
        if health_fraction > 1:
            health_crop = 16 + int(7 * (player.hearts - Settings.PLAYER_HEARTS))
            self.alt_health_bar.render(surface, (10, 6),
                                size=(0, 0, health_crop*2, 17*2), delta=delta)
        
        # Display outline for each extra life unlocked even if unfilled
        if num_challenges > 0:  
            health_crop = 16 + int(7 * num_challenges)
            dirty_rects += self.health_outline_alt.render(surface, (10, 6), 
                size=(0, 0, health_crop*2, 17*2))

        # Draw base outline
        dirty_rects += self.health_outline.render(
            surface, pygame.Vector2(10, 10))

        # Render save hint if player can save at player position
        if player.can_save:
            dirty_rects += self.save_sprite.render(
                surface, offset + player.position)
        # Always draw save animation since first and last frame are empty so only visible during animation
        dirty_rects += self.save_animation.render(surface, delta=delta)

        return dirty_rects

    def handle_events(self, events):
        """ Process events for GUI. Returns tuple representing the gui state.
        Tuple: (is game running, is pause menu open, is any title menu open, 
        save number player selected to load, does display need to be restarted, 
        players choosen name, has player left end game gui)

        Args:
            events ([pygame.events.Events]): List of pygame events to be processed (required).
        """

        # Setup states to be returned
        running, restart, name, leave_endgame = True, False, None, None

        # Process each event
        for event in events:
            if event.type == pygame.USEREVENT:
                # Proccess left click on gui elements
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    # Handle each navigation button eg. quit to title
                    if event.ui_element == self.menus["paused"]["resume"]:
                        self.set_state()
                    elif event.ui_element == self.menus["paused"]["settings"]:
                        self.set_state("settings")
                    elif event.ui_element == self.menus["paused"]["quit"]:
                        self.set_state("title")
                    elif event.ui_element == self.menus["end_game"]["quit"]:
                        self.set_state("title")
                        leave_endgame = True
                    elif event.ui_element == self.menus["title"]["quit"]:
                        # Quiting in title exits gameloop
                        running = False
                    elif event.ui_element == self.menus["title"]["new_game"]:
                        self.set_state("select_save")
                    elif event.ui_element == self.menus["title"]["settings"]:
                        self.set_state("title_settings")
                    elif event.ui_element == self.menus["select_save"]["back"]:
                        self.set_state("title")
                    
                    # Handle saving new settings from title menu
                    elif event.ui_element == self.menus["title_settings"]["save"]:
                        # Return to title
                        self.set_state("title")

                        # Map choosen aspect ratio to resolution
                        new_resolution = ["1100x300", "800x340", "770x430", "600x380", "660x500"][[
                            "11:3", "21:9", "16:9", "16:10", "4:3"].index(self.menus["title_settings"]["resolution"].selected_option)]

                        # Update global music and user settings objects
                        Settings.USER_SETTINGS["music_volume"] = self.menus["title_settings"]["music_volume"].get_current_value(
                        )
                        # Scale each sound by its new volume
                        for key, sound in Settings.MUSIC.items():
                            if Settings.USER_SETTINGS["music"]:
                                vol = Settings.USER_SETTINGS["music_volume"] * (
                                    Settings.MUSIC_VOLUMES[key] / 100)
                                sound.SetVolume(vol)
                            else:
                                sound.SetVolume(0)

                        # Update global music and user settings objects
                        Settings.USER_SETTINGS["sound_effects_volume"] = self.menus["title_settings"]["sound_effects_volume"].get_current_value(
                        )
                        # Scale each sound by its new volume
                        for key, sound in Settings.SOUND_EFFECTS.items():
                            if Settings.USER_SETTINGS["sound_effects"]:
                                vol = Settings.USER_SETTINGS["sound_effects_volume"] * (
                                    Settings.SOUND_EFFECTS_VOLUMES[key] / 100)
                                sound.SetVolume(vol)
                            else:
                                sound.SetVolume(0)

                        # If resolution was changed or display made fullscreen the display needs to be updated
                        if (not Settings.USER_SETTINGS["resolution"] == new_resolution) or (not Settings.is_fullscreen == Settings.USER_SETTINGS["fullscreen"]):
                            restart = True
                        Settings.USER_SETTINGS["resolution"] = new_resolution

                        # Attempt to write new user settings file
                        try:
                            with open(Settings.USER_SETTINGS_PATH, 'w') as file:
                                json.dump(Settings.USER_SETTINGS, file)
                        except Exception as e:
                            if Settings.DEBUG:
                                print("Failed to write user settings", e)
                    # Handle each of the settings toggle buttons to switch between ON and OFF and update settings
                    elif event.ui_element == self.menus["title_settings"]["fullscreen"]:
                        Settings.USER_SETTINGS["fullscreen"] = not Settings.USER_SETTINGS["fullscreen"]
                        self.menus["title_settings"]["fullscreen"].set_text(
                            ["OFF", "ON"][Settings.USER_SETTINGS["fullscreen"]])
                    elif event.ui_element == self.menus["title_settings"]["music"]:
                        Settings.USER_SETTINGS["music"] = not Settings.USER_SETTINGS["music"]
                        self.menus["title_settings"]["music"].set_text(
                            ["OFF", "ON"][Settings.USER_SETTINGS["music"]])
                    elif event.ui_element == self.menus["title_settings"]["sound_effects"]:
                        Settings.USER_SETTINGS["sound_effects"] = not Settings.USER_SETTINGS["sound_effects"]
                        self.menus["title_settings"]["sound_effects"].set_text(
                            ["OFF", "ON"][Settings.USER_SETTINGS["sound_effects"]])
                    # Handle each button to load a save
                    elif event.ui_element == self.menus["select_save"]["save1"]:
                        self.selected_save = 1
                        # If save hasnt begun prompt user for a name
                        if not self.has_begun[0]:
                            self.set_state("name")
                        else:
                            self.set_state()
                    elif event.ui_element == self.menus["select_save"]["save2"]:
                        self.selected_save = 2
                        if not self.has_begun[1]:
                            self.set_state("name")
                        else:
                            self.set_state()
                    elif event.ui_element == self.menus["select_save"]["save3"]:
                        self.selected_save = 3
                        if not self.has_begun[2]:
                            self.set_state("name")
                        else:
                            self.set_state()
                    # Handle naming menu by setting name when player continues and entering game
                    elif event.ui_element == self.menus["name"]["continue"]:
                        name = self.menus["name"]["entry"].get_text()
                        self.set_state()
                    # Update user settings file after changing bindings and saving
                    elif event.ui_element == self.menus["settings"]["save"] and not ("binding" in self.state):
                        self.set_state("paused")
                        try:
                            with open(Settings.USER_SETTINGS_PATH, 'w') as file:
                                json.dump(Settings.USER_SETTINGS, file)
                        except:
                            print("Failed to write user settings")
                    # Match each button in control menu to bind the correct action and set state
                    elif event.ui_element == self.menus["settings"]["attack"] and not ("binding" in self.state):
                        self.set_state("settings", "binding")
                        self.to_bind_key = "attack"
                    elif event.ui_element == self.menus["settings"]["jump"] and not ("binding" in self.state):
                        self.set_state("settings", "binding")
                        self.to_bind_key = "jump"
                    elif event.ui_element == self.menus["settings"]["left"] and not ("binding" in self.state):
                        self.set_state("settings", "binding")
                        self.to_bind_key = "left"
                    elif event.ui_element == self.menus["settings"]["right"] and not ("binding" in self.state):
                        self.set_state("settings", "binding")
                        self.to_bind_key = "right"
                    elif event.ui_element == self.menus["settings"]["up"] and not ("binding" in self.state):
                        self.set_state("settings", "binding")
                        self.to_bind_key = "up"
                    elif event.ui_element == self.menus["settings"]["down"] and not ("binding" in self.state):
                        self.set_state("settings", "binding")
                        self.to_bind_key = "down"
                    elif event.ui_element == self.menus["settings"]["dialog"] and not ("binding" in self.state):
                        self.set_state("settings", "binding")
                        self.to_bind_key = "dialog"
            # Procces escape key to exit menus
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Pause when in game
                    if len(self.state) == 0:
                        self.set_state("paused")
                    # Unpause
                    elif ("paused" in self.state):
                        self.set_state()
                    # Return to save from control menu and save modifications
                    elif ("settings" in self.state):
                        self.set_state("paused")
                        try:
                            with open(Settings.USER_SETTINGS_PATH, 'w') as file:
                                json.dump(Settings.USER_SETTINGS, file)
                        except:
                            print("Failed to write user settings")
                    # Exit binding state without changing binding
                    elif ("binding" in self.state):
                        self.set_state("settings")
                # For all non escape keys check if binding and if so bind new key to one just pressed
                elif ("binding" in self.state):
                    # Get key name from pygame
                    Settings.USER_SETTINGS["bindings"][self.to_bind_key] = pygame.key.name(
                        event.key)
                    # Update settings
                    self.menus["settings"][self.to_bind_key].set_text(
                        pygame.key.name(event.key).upper())
                    # Exit binding state
                    self.set_state("settings")
        # Return tuple representing gui state
        return (running, not len(self.state) == 0,  ("title" in self.state) or ("select_save" in self.state) or ("title_settings" in self.state) or ("name" in self.state), self.selected_save, restart, name, leave_endgame)

    def render(self, surface, delta):
        """ Draw sprites associated with gui to surface. Lies under gui elements.

        Args:
            surface (pygame.Surface): Surface to render to in gui space.
            delta (float): Time since last render call, used for animations.
        """
        # Draw title background animation if in any title
        if ("title" in self.state) or ("select_save" in self.state) or ("title_settings" in self.state) or ("name" in self.state) or ("end_game" in self.state):
            self.title_background.render(
                surface, pygame.Vector2(0, 0), delta=delta)
        # Only draw logo animation on endgame and title screen
        if ("title" in self.state) or ("end_game" in self.state):
            self.title_animation.render(surface, delta=delta)

    def set_state(self, *state):
        """ Update gui state, changes visibility of elements and sprites.

        Args:
            *state (str): Variadic argument for setting any number of gui states together.
        """
        # Show all menus which are in list of state, otherwise hide
        self.state = state
        for name, menu in self.menus.items():
            if name in state:
                for el in menu.values():
                    el.show()
            else:
                for el in menu.values():
                    el.hide()

        # If list of states contain any title menu's show title background animation
        if set(["title_settings", "title", "select_save", "name"]).intersection(state):
            self.title_background.show()
        else:
            self.title_background.hide()

        # Hide mouse cursor during gameplay
        pygame.mouse.set_visible(bool(set(
            ["paused", "settings",  "binding",  "title",  "select_save",  "title_settings", "name", "end_game"]).intersection(state)))
