import pygame, pygame_gui, json
from pygame.transform import scale
from Packages import Settings, Sprite


class Gui():
    """ """
    def __init__(self, health_spritesheet_filename, health_sprite_filename, title_image_filename, title_background_filename, save_sprite_filename, save_animation_filename, state=None):
        self.focused = 0

        title_surface = pygame.image.load(title_image_filename).convert_alpha()
        scale = max(Settings.RESOLUTION[0] / 700, Settings.RESOLUTION[1] / 394)
        self.title_background = Sprite.AnimatedSprite(spritesheet_json_filename=title_background_filename, spritesheet_scale=(scale,scale))
        self.title_background.play_animation("loop", loop=-1)
        self.title_gui = {
            # "background": pygame_gui.elements.UIImage(
            #     relative_rect=pygame.Rect((0, 0), Settings.RESOLUTION),
            #     image_surface=pygame.image.load(
            #         title_background_filename).convert_alpha(),
            #     manager=Settings.gui_manager
            # ),
            "logo": pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect(
                    (Settings.RESOLUTION[0] / 2 - 327/2, 90), [327, 66]),
                image_surface=title_surface,
                manager=Settings.gui_manager,
            ),
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
        }

        vertical_gap, vertical_height = 40, 30
        self.completions = []
        for i in range(3):
            save_filename = Settings.SAVE_FILETEMPLATE.substitute(num=str(i+1))
            try:
                with open(save_filename) as json_file:
                    json_data = json.load(json_file)
                self.completions.append(json_data["title_info"]["percentage_completion"])
            except Exception as e:
                if Settings.DEBUG:
                    print(f"Failed to load save {save_filename}, error: ", e)
                self.completions.append(0)
        self.select_save_gui = {
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
        }

        self.paused_gui = {
            "panel": pygame_gui.elements.UIPanel(relative_rect=pygame.Rect((0, 0), Settings.RESOLUTION), starting_layer_height=-1, manager=Settings.gui_manager),
            "resume": pygame_gui.elements.UIButton(starting_height=2,relative_rect=pygame.Rect((Settings.RESOLUTION[0]/2-50, Settings.RESOLUTION[1]/2-100), (200, 50)), text="RESUME", manager=Settings.gui_manager),
            "settings": pygame_gui.elements.UIButton(starting_height=2,relative_rect=pygame.Rect((Settings.RESOLUTION[0]/2-50, Settings.RESOLUTION[1]/2-40), (200, 50)), text="CONTROLS", manager=Settings.gui_manager),
            "quit": pygame_gui.elements.UIButton(starting_height=2,relative_rect=pygame.Rect((Settings.RESOLUTION[0]/2-50, Settings.RESOLUTION[1]/2+20), (200, 50)), text="TO TITLE", manager=Settings.gui_manager),
        }
        self.paused_focus = ["resume", "settings", "quit"]
        vertical_gap, vertical_height = 40, 30
        self.settings_gui = {
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
                text=Settings.USER_SETTINGS["bindings"]["attack"].upper(),
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
                text=Settings.USER_SETTINGS["bindings"]["jump"].upper(),
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
                text=Settings.USER_SETTINGS["bindings"]["left"].upper(),
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
                text=Settings.USER_SETTINGS["bindings"]["right"].upper(),
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
                text=Settings.USER_SETTINGS["bindings"]["up"].upper(),
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
                text=Settings.USER_SETTINGS["bindings"]["down"].upper(),
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
                text=Settings.USER_SETTINGS["bindings"]["dialog"].upper(),
                object_id='#small_button',
                manager=Settings.gui_manager
            ),
            "save": pygame_gui.elements.UIButton(starting_height=2,
                relative_rect=pygame.Rect(
                    (Settings.RESOLUTION[0]/2-170, Settings.RESOLUTION[1]*8/9-25), (200, 50)),
                text="SAVE",
                manager=Settings.gui_manager
            ),
        }
        
        self.title_settings_gui = {
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
                text=["OFF", "ON"][Settings.USER_SETTINGS["fullscreen"]],
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
                options_list=["1100x300","800x340","770x430", "600x380", "660x500"],
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
                text=["OFF", "ON"][Settings.USER_SETTINGS["music"]],
                object_id="#small_button",
                manager=Settings.gui_manager,
            ),
            "music_volume": pygame_gui.elements.UIHorizontalSlider(
                start_value=Settings.USER_SETTINGS["music_volume"],
                value_range=(0,100),
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
                text=["OFF", "ON"][Settings.USER_SETTINGS["sound_effects"]],
                object_id="#small_button",
                manager=Settings.gui_manager,
            ),
            "sound_effects_volume": pygame_gui.elements.UIHorizontalSlider(
                start_value=Settings.USER_SETTINGS["sound_effects_volume"],
                value_range=(0,100),
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
        }

        self.binding_gui = {
            "panel": pygame_gui.elements.UIPanel(relative_rect=pygame.Rect((0, 0), Settings.RESOLUTION), starting_layer_height=1, manager=Settings.gui_manager),
            "key_label": pygame_gui.elements.UILabel(
                text="Press Key",
                relative_rect=pygame.Rect(
                    (Settings.RESOLUTION[0]/2-200, Settings.RESOLUTION[1]/2-25), (400, 50)),
                manager=Settings.gui_manager
            ),
        }
        self.to_bind_key = ""

        if not state == None:
            self.state = state
            self.set_state(pause=self.state == "paused",
                           settings=self.state == "settings")
        else:
            self.state = "none"
            self.set_state()

        self.health_bar = Sprite.AnimatedSprite(
            spritesheet_json_filename=health_spritesheet_filename, spritesheet_scale=(3, 3))
        self.health_bar.play_animation("idle", loop=True)
        self.health_outline = Sprite.ImageSprite(
            health_sprite_filename, scale=(3, 3))
        self.health_outline.z = 2
        self.save_sprite = Sprite.ImageSprite(save_sprite_filename, scale=(1, 1))
        self.save_animation = Sprite.AnimatedSprite(spritesheet_json_filename=save_animation_filename, position=pygame.Vector2(0, Settings.RESOLUTION[1]-64))

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
        self.health_bar.render(surface, (10,10),
                               size=(0, 0, health_crop*3, 17*3), delta=delta)
        dirty_rects += self.health_outline.render(surface, pygame.Vector2(10, 10))

        # Render save icon
        if player.can_save:
            dirty_rects += self.save_sprite.render(surface, offset + player.position)
        dirty_rects += self.save_animation.render(surface, delta=delta)

        return dirty_rects

    def handle_events(self, events):
        """

        :param events: 

        """
        running, selected_save, restart = True, None, False
        for event in events:
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.paused_gui["resume"]:
                        self.set_state(pause=False)
                    elif event.ui_element == self.paused_gui["settings"]:
                        self.set_state(settings=True)
                    elif event.ui_element == self.paused_gui["quit"]:
                        self.set_state(title=True)
                    elif event.ui_element == self.title_gui["quit"]:
                        running = False
                    elif event.ui_element == self.title_gui["new_game"]:
                        self.set_state(select_save=True)
                    elif event.ui_element == self.title_gui["settings"]:
                        self.set_state(title_settings=True)

                    elif event.ui_element == self.title_settings_gui["save"]:
                        self.set_state(title=True)

                        # Update settings
                        Settings.USER_SETTINGS["music_volume"] = self.title_settings_gui["music_volume"].get_current_value()
                        for key, sound in Settings.MUSIC.items():
                            if Settings.USER_SETTINGS["music"]:
                                vol = Settings.USER_SETTINGS["music_volume"] * (Settings.MUSIC_VOLUMES[key] / 100)
                                sound.SetVolume(vol)
                            else:
                                sound.SetVolume(0)
                        
                        Settings.USER_SETTINGS["sound_effects_volume"] = self.title_settings_gui["sound_effects_volume"].get_current_value()
                        for key, sound in Settings.SOUND_EFFECTS.items():
                            if Settings.USER_SETTINGS["sound_effects"]:
                                vol = Settings.USER_SETTINGS["sound_effects_volume"] * (Settings.SOUND_EFFECTS_VOLUMES[key] / 100)
                                sound.SetVolume(vol)
                            else:
                                sound.SetVolume(0)
                        
                        if (not Settings.USER_SETTINGS["resolution"] == self.title_settings_gui["resolution"].selected_option) or (not Settings.is_fullscreen == Settings.USER_SETTINGS["fullscreen"]):
                            restart = True

                        Settings.USER_SETTINGS["resolution"] = self.title_settings_gui["resolution"].selected_option
                        try:
                            with open(Settings.USER_SETTINGS_PATH, 'w') as file:
                                json.dump(Settings.USER_SETTINGS, file)
                        except:
                            print("Failed to write user settings")

                    elif event.ui_element == self.title_settings_gui["fullscreen"]:
                        Settings.USER_SETTINGS["fullscreen"] = not Settings.USER_SETTINGS["fullscreen"]
                        self.title_settings_gui["fullscreen"].set_text(
                            ["OFF", "ON"][Settings.USER_SETTINGS["fullscreen"]])
                    elif event.ui_element == self.title_settings_gui["music"]:
                        Settings.USER_SETTINGS["music"] = not Settings.USER_SETTINGS["music"]
                        self.title_settings_gui["music"].set_text(
                            ["OFF", "ON"][Settings.USER_SETTINGS["music"]])
                    elif event.ui_element == self.title_settings_gui["sound_effects"]:
                        Settings.USER_SETTINGS["sound_effects"] = not Settings.USER_SETTINGS["sound_effects"]
                        self.title_settings_gui["sound_effects"].set_text(
                            ["OFF", "ON"][Settings.USER_SETTINGS["sound_effects"]])
                    elif event.ui_element == self.select_save_gui["save1"]:
                        selected_save = 1
                        self.set_state()
                    elif event.ui_element == self.select_save_gui["save2"]:
                        selected_save = 2
                        self.set_state()
                    elif event.ui_element == self.select_save_gui["save3"]:
                        selected_save = 3
                        self.set_state()
                    elif event.ui_element == self.select_save_gui["back"]:
                        self.set_state(title=True)

                    elif event.ui_element == self.settings_gui["save"] and not self.state == "binding":
                        self.set_state(pause=True)
                        try:
                            with open(Settings.USER_SETTINGS_PATH, 'w') as file:
                                json.dump(Settings.USER_SETTINGS, file)
                        except:
                            print("Failed to write user settings")
                    elif event.ui_element == self.settings_gui["attack"] and not self.state == "binding":
                        self.set_state(settings=True, binding=True)
                        self.to_bind_key = "attack"
                    elif event.ui_element == self.settings_gui["jump"] and not self.state == "binding":
                        self.set_state(settings=True, binding=True)
                        self.to_bind_key = "jump"
                    elif event.ui_element == self.settings_gui["left"] and not self.state == "binding":
                        self.set_state(settings=True, binding=True)
                        self.to_bind_key = "left"
                    elif event.ui_element == self.settings_gui["right"] and not self.state == "binding":
                        self.set_state(settings=True, binding=True)
                        self.to_bind_key = "right"
                    elif event.ui_element == self.settings_gui["up"] and not self.state == "binding":
                        self.set_state(settings=True, binding=True)
                        self.to_bind_key = "up"
                    elif event.ui_element == self.settings_gui["down"] and not self.state == "binding":
                        self.set_state(settings=True, binding=True)
                        self.to_bind_key = "down"
                    elif event.ui_element == self.settings_gui["dialog"] and not self.state == "binding":
                        self.set_state(settings=True, binding=True)
                        self.to_bind_key = "dialog"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "none":
                        self.set_state(pause=True)
                    elif self.state == "paused":
                        self.set_state(pause=False)
                    elif self.state == "settings":
                        self.set_state(pause=True)
                        try:
                            with open(Settings.USER_SETTINGS_PATH, 'w') as file:
                                json.dump(Settings.USER_SETTINGS, file)
                        except:
                            print("Failed to write user settings")
                    elif self.state == "binding":
                        self.set_state(settings=True)
                # elif event.key == pygame.K_DOWN:
                #     if self.state == "settings":
                #         for i in range(len(self.settings_focus)):
                #             self.settings_gui[self.settings_focus[i]].unselect()
                #         self.focused = (self.focused + 1) % len(self.settings_focus)
                #         self.settings_gui[self.settings_focus[self.focused]].select()
                #     elif self.state == "paused":
                #         for i in range(len(self.paused_focus)):
                #             self.paused_gui[self.paused_focus[i]].unselect()
                #         self.focused = (self.focused + 1) % len(self.paused_focus)
                #         self.paused_gui[self.paused_focus[self.focused]].select()
                # elif event.key == pygame.K_UP:
                #     if self.state == "settings":
                #         for i in range(len(self.settings_focus)):
                #             self.settings_gui[self.settings_focus[i]].unselect()
                #         self.focused = min(self.focused - 1, len(self.settings_focus) - 1)
                #         self.settings_gui[self.settings_focus[self.focused]].select()
                #     elif self.state == "paused":
                #         for i in range(len(self.paused_focus)):
                #             self.paused_gui[self.paused_focus[i]].unselect()
                #         self.focused = min(self.focused - 1, len(self.paused_focus) - 1)
                #         self.paused_gui[self.paused_focus[self.focused]].select()
                elif self.state == "binding":
                    Settings.USER_SETTINGS["bindings"][self.to_bind_key] = pygame.key.name(
                        event.key)
                    self.settings_gui[self.to_bind_key].set_text(
                        pygame.key.name(event.key).upper())
                    self.set_state(settings=True)
                # elif event.key == pygame.K_RETURN:
                #     if self.state == "settings":
                #         element = self.settings_gui[self.settings_focus[self.focused]]
                #         pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"user_type":pygame_gui.UI_BUTTON_PRESSED, "ui_element":element}))
                #     elif self.state == "paused":
                #         element = self.paused_gui[self.paused_focus[self.focused]]
                #         pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"user_type":pygame_gui.UI_BUTTON_PRESSED, "ui_element":element}))

        return (running, not self.state == "none", self.state == "title" or self.state == "select_save" or self.state=="title_settings", selected_save, restart)

    def render(self, surface, offset, delta):
        """

        :param surface: 
        :param offset: 
        :param delta: 

        """
        if self.state == "title" or self.state == "select_save" or self.state == "title_settings":
            self.title_background.render(surface, pygame.Vector2(0,0), delta=delta)

    def set_state(self, pause=False, settings=False, binding=False, title=False, select_save=False, title_settings=False):
        """

        :param pause:  (Default value = False)
        :param settings:  (Default value = False)
        :param binding:  (Default value = False)
        :param title:  (Default value = False)
        :param select_save:  (Default value = False)
        :param title_settings:  (Default value = False)

        """
        self.state = [False, "select_save"][select_save] or [False, "title"][title] or [
            False, "binding"][binding] or [False, "settings"][settings] or [False, "paused"][pause] or [False, "title_settings"][title_settings]
        if self.state == False:
            self.state = "none"
        #self.focused = 0
        if binding:
            for element in self.binding_gui.values():
                element.show()
        else:
            for element in self.binding_gui.values():
                element.hide()
        if settings:
            for element in self.settings_gui.values():
                element.show()
        else:
            for element in self.settings_gui.values():
                element.hide()
        if pause:
            for element in self.paused_gui.values():
                element.show()
        else:
            for element in self.paused_gui.values():
                element.hide()
        if title:
            for element in self.title_gui.values():
                element.show()
        else:
            for element in self.title_gui.values():
                element.hide()
        if select_save:
            for element in self.select_save_gui.values():
                element.show()
        else:
            for element in self.select_save_gui.values():
                element.hide()
        if title_settings:
            for element in self.title_settings_gui.values():
                element.show()
        else:
            for element in self.title_settings_gui.values():
                element.hide()

        if title_settings or title or select_save:
            self.title_background.show()
        else:
            self.title_background.hide()

        pygame.mouse.set_visible(
            pause or settings or binding or title or select_save or title_settings)
