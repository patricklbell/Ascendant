import pygame
import pygame_gui
import json
from Packages import Settings, Sprite


class Gui():
    """ """

    def __init__(self, health_spritesheet_filename, health_sprite_filename, title_animation_filename, title_background_filename, save_sprite_filename, save_animation_filename, state=None):
        self.to_bind_key = ""
        self.selected_save = 0

        scale = max(Settings.RESOLUTION[0] / 700, Settings.RESOLUTION[1] / 394)
        self.title_background = Sprite.AnimatedSprite(
            spritesheet_json_filename=title_background_filename, spritesheet_scale=(scale, scale))
        self.title_background.play_animation("loop", loop=-1)

        self.title_animation = Sprite.AnimatedSprite(position=pygame.Vector2(
            Settings.RESOLUTION[0]/2-280/2, 75), spritesheet_json_filename=title_animation_filename, spritesheet_scale=(0.25, 0.25))
        self.title_animation.play_animation("loop", loop=-1)

        self.health_bar = Sprite.AnimatedSprite(
            spritesheet_json_filename=health_spritesheet_filename, spritesheet_scale=(3, 3))
        self.health_bar.play_animation("idle", loop=True)
        self.health_outline = Sprite.ImageSprite(
            health_sprite_filename, scale=(3, 3))
        self.health_outline.z = 2
        self.save_sprite = Sprite.ImageSprite(
            save_sprite_filename, scale=(1, 1))
        self.save_animation = Sprite.AnimatedSprite(
            spritesheet_json_filename=save_animation_filename, position=pygame.Vector2(0, Settings.RESOLUTION[1]-64))

        vertical_gap, vertical_height = 40, 30
        self.completions = []
        self.has_begun = []
        for i in range(3):
            save_filename = Settings.SAVE_FILETEMPLATE.substitute(num=str(i+1))
            try:
                with open(save_filename) as json_file:
                    json_data = json.load(json_file)
                self.completions.append(
                    json_data["title_info"]["percentage_completion"])
                self.has_begun.append(json_data["has_begun"])
            except FileNotFoundError as e:
                if Settings.DEBUG:
                    print(f"Failed to load save {save_filename}, error: ", e)
                self.completions.append(0)
                self.has_begun.append(False)

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
            "select_save": {
                "save1_label": pygame_gui.elements.UILabel(
                    text=f"SAVE 1 ({self.completions[0]}%):",
                    object_id='#small_label',
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2-200, Settings.RESOLUTION[1]/3), (200, vertical_height)),
                    manager=Settings.gui_manager
                ),
                "save1": pygame_gui.elements.UIButton(
                    text="CONTINUE",
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2, Settings.RESOLUTION[1]/3), (200, vertical_height)),
                    object_id='#small_button',
                    manager=Settings.gui_manager,
                    starting_height=2,
                ),
                "save2_label": pygame_gui.elements.UILabel(
                    text=f"SAVE 2 ({self.completions[1]}%):",
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2-200, Settings.RESOLUTION[1]/3+vertical_gap), (200, vertical_height)),
                    object_id='#small_label',
                    manager=Settings.gui_manager
                ),
                "save2": pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2, Settings.RESOLUTION[1]/3+vertical_gap), (200, vertical_height)),
                    text="CONTINUE",
                    object_id='#small_button',
                    manager=Settings.gui_manager,
                    starting_height=2,
                ),
                "save3_label": pygame_gui.elements.UILabel(
                    text=f"SAVE 3 ({self.completions[2]}%):",
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2-200, Settings.RESOLUTION[1]/3+vertical_gap*2), (200, vertical_height)),
                    object_id='#small_label',
                    manager=Settings.gui_manager,
                ),
                "save3": pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2, Settings.RESOLUTION[1]/3+vertical_gap*2), (200, vertical_height)),
                    text="CONTINUE",
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
                    text="RESOLUTION",
                    relative_rect=pygame.Rect(
                        (Settings.RESOLUTION[0]/2-200, Settings.RESOLUTION[1]/6+vertical_gap), (200, vertical_height)),
                    object_id="#small_label",
                    manager=Settings.gui_manager
                ),
                "resolution": pygame_gui.elements.UIDropDownMenu(
                    # options_list=["1120x315","808x342","772x433", "592x370", "660x495"],
                    # options_list=["1280x360","850x360","820x460", "640x400", "700x525"],
                    options_list=["1100x300", "800x340",
                                  "770x430", "600x380", "660x500"],
                    starting_option=Settings.RESOLUTION_STR,
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

    def render_ingame(self, delta, surface, player, offset=pygame.Vector2(0, 0)):
        """

        :param delta: 
        :param surface: 
        :param player: 
        :param offset:  (Default value = pygame.Vector2(0,0))

        """
        dirty_rects = []

        health_fraction = (player.hearts-1) / (Settings.PLAYER_HEARTS-1)
        if player.hearts == 0:
            health_fraction = 0

        # Crop health to show fraction
        if health_fraction == 0:
            health_crop = 0
        else:
            health_crop = 16 + int(42*health_fraction)
        self.health_bar.render(surface, (10, 10),
                               size=(0, 0, health_crop*3, 17*3), delta=delta)
        dirty_rects += self.health_outline.render(
            surface, pygame.Vector2(10, 10))

        # Render save icon
        if player.can_save:
            dirty_rects += self.save_sprite.render(
                surface, offset + player.position)
        dirty_rects += self.save_animation.render(surface, delta=delta)

        return dirty_rects

    def handle_events(self, events):
        """

        :param events: 

        """
        running, restart, name = True, False, None
        for event in events:
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.menus["paused"]["resume"]:
                        self.set_state()
                    elif event.ui_element == self.menus["paused"]["settings"]:
                        self.set_state("settings")
                    elif event.ui_element == self.menus["paused"]["quit"]:
                        self.set_state("title")
                    elif event.ui_element == self.menus["title"]["quit"]:
                        running = False
                    elif event.ui_element == self.menus["title"]["new_game"]:
                        self.set_state("select_save")
                    elif event.ui_element == self.menus["title"]["settings"]:
                        self.set_state("title_settings")

                    elif event.ui_element == self.menus["title_settings"]["save"]:
                        self.set_state("title")

                        # Update settings
                        Settings.USER_SETTINGS["music_volume"] = self.menus["title_settings"]["music_volume"].get_current_value(
                        )
                        for key, sound in Settings.MUSIC.items():
                            if Settings.USER_SETTINGS["music"]:
                                vol = Settings.USER_SETTINGS["music_volume"] * (
                                    Settings.MUSIC_VOLUMES[key] / 100)
                                sound.SetVolume(vol)
                            else:
                                sound.SetVolume(0)

                        Settings.USER_SETTINGS["sound_effects_volume"] = self.menus["title_settings"]["sound_effects_volume"].get_current_value(
                        )
                        for key, sound in Settings.SOUND_EFFECTS.items():
                            if Settings.USER_SETTINGS["sound_effects"]:
                                vol = Settings.USER_SETTINGS["sound_effects_volume"] * (
                                    Settings.SOUND_EFFECTS_VOLUMES[key] / 100)
                                sound.SetVolume(vol)
                            else:
                                sound.SetVolume(0)

                        if (not Settings.USER_SETTINGS["resolution"] == self.menus["title_settings"]["resolution"].selected_option) or (not Settings.is_fullscreen == Settings.USER_SETTINGS["fullscreen"]):
                            restart = True

                        Settings.USER_SETTINGS["resolution"] = self.menus["title_settings"]["resolution"].selected_option
                        try:
                            with open(Settings.USER_SETTINGS_PATH, 'w') as file:
                                json.dump(Settings.USER_SETTINGS, file)
                        except:
                            print("Failed to write user settings")

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
                    elif event.ui_element == self.menus["select_save"]["save1"]:
                        self.selected_save = 1
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
                    elif event.ui_element == self.menus["name"]["continue"]:
                        name = self.menus["name"]["entry"].get_text()
                        self.set_state()
                    elif event.ui_element == self.menus["select_save"]["back"]:
                        self.set_state("title")
                    elif event.ui_element == self.menus["settings"]["save"] and not ("binding" in self.state):
                        self.set_state("paused")
                        try:
                            with open(Settings.USER_SETTINGS_PATH, 'w') as file:
                                json.dump(Settings.USER_SETTINGS, file)
                        except:
                            print("Failed to write user settings")
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

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if len(self.state) == 0:
                        self.set_state("paused")
                    elif ("paused" in self.state):
                        self.set_state()
                    elif ("settings" in self.state):
                        self.set_state("paused")
                        try:
                            with open(Settings.USER_SETTINGS_PATH, 'w') as file:
                                json.dump(Settings.USER_SETTINGS, file)
                        except:
                            print("Failed to write user settings")
                    elif ("binding" in self.state):
                        self.set_state("settings")
                # elif event.key == pygame.K_DOWN:
                #     if  ("settings" in self.state):
                #         for i in range(len(self.settings_focus)):
                #             self.menus["settings"][self.settings_focus[i]].unselect()
                #         self.focused = (self.focused + 1) % len(self.settings_focus)
                #         self.menus["settings"][self.settings_focus[self.focused]].select()
                #     elif  ("paused" in self.state):
                #         for i in range(len(self.paused_focus)):
                #             self.menus["paused"][self.paused_focus[i]].unselect()
                #         self.focused = (self.focused + 1) % len(self.paused_focus)
                #         self.menus["paused"][self.paused_focus[self.focused]].select()
                # elif event.key == pygame.K_UP:
                #     if  ("settings" in self.state):
                #         for i in range(len(self.settings_focus)):
                #             self.menus["settings"][self.settings_focus[i]].unselect()
                #         self.focused = min(self.focused - 1, len(self.settings_focus) - 1)
                #         self.menus["settings"][self.settings_focus[self.focused]].select()
                #     elif  ("paused" in self.state):
                #         for i in range(len(self.paused_focus)):
                #             self.menus["paused"][self.paused_focus[i]].unselect()
                #         self.focused = min(self.focused - 1, len(self.paused_focus) - 1)
                #         self.menus["paused"][self.paused_focus[self.focused]].select()
                elif ("binding" in self.state):
                    Settings.USER_SETTINGS["bindings"][self.to_bind_key] = pygame.key.name(
                        event.key)
                    self.menus["settings"][self.to_bind_key].set_text(
                        pygame.key.name(event.key).upper())
                    self.set_state("settings")
                # elif event.key == pygame.K_RETURN:
                #     if  ("settings" in self.state):
                #         element = self.menus["settings"][self.settings_focus[self.focused]]
                #         pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"user_type":pygame_gui.UI_BUTTON_PRESSED, "ui_element":element}))
                #     elif  ("paused" in self.state):
                #         element = self.menus["paused"][self.paused_focus[self.focused]]
                #         pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"user_type":pygame_gui.UI_BUTTON_PRESSED, "ui_element":element}))

        return (running, not len(self.state) == 0,  ("title" in self.state) or ("select_save" in self.state) or ("title_settings" in self.state) or ("name" in self.state), self.selected_save, restart, name)

    def render(self, surface, offset, delta):
        """

        :param surface: 
        :param offset: 
        :param delta: 

        """
        if ("title" in self.state) or ("select_save" in self.state) or ("title_settings" in self.state) or ("name" in self.state):
            self.title_background.render(
                surface, pygame.Vector2(0, 0), delta=delta)
            if ("title" in self.state):
                self.title_animation.render(surface, delta=delta)

    def set_state(self, *state):
        """
        :param state:  (Default value = [])

        """
        self.state = state
        for name, menu in self.menus.items():
            if name in state:
                for el in menu.values():
                    el.show()
            else:
                for el in menu.values():
                    el.hide()

        if set(["title_settings", "title", "select_save", "name"]).intersection(state):
            self.title_background.show()
        else:
            self.title_background.hide()

        pygame.mouse.set_visible(bool(set(
            ["paused", "settings",  "binding",  "title",  "select_save",  "title_settings", "name"]).intersection(state)))
