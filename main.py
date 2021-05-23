from typing import Set
import pygame_gui
import pygame
from Packages import Settings, Level, Player, Gui, Enemy, Water, Console
import os
import warnings
import pickle
import copy
import platform
import json
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
warnings.simplefilter('ignore')

if platform.system() == "Windows":
    import ctypes

level, debug_console = None, None


def init():
    global level, debug_console
    Settings.init()
    level = Level.Level(
        should_load=False,
        player_base=Player.Player(
            spritesheet_json_filename=Settings.SRC_DIRECTORY +
            "Entities/Player/player_spritesheet.json",
            spritesheet_scale=(1.75, 1.75),
            collider_offset=pygame.Vector2(57*0.875, 60*0.875),
            collider_size=pygame.Vector2(14*0.875, 34*0.875),
            gravity=pygame.Vector2(0, 1500),
            walk_speed=150,
            water_walk_speed=120,
            jump_speed=-300,
            jump_add_speed=-1200,
            jump_add_max_time=0.3,
            jump_grace_frames=4,
            knockback_speed=pygame.Vector2(200, 500),
            bounce_speed=pygame.Vector2(400, 500),
            damage_knockback_speed=100,
            attack0_length=34*0.875,
            attack1_length=35*0.875,
            attack2_length=10*0.875,
            attack0_width=-2*0.875,
            attack1_width=50*0.875,
            attack2_width=50*0.875,
            hearts=Settings.PLAYER_HEARTS,
            iframes=90,
            calculate_flip=True,
            calculate_white=True,
            water_splash_json_filename=Settings.SRC_DIRECTORY +
            "Entities/Water/splash_spritesheet.json",
            water_big_splash_json_filename=Settings.SRC_DIRECTORY +
            "Entities/Water/big_splash_spritesheet.json",
            short_stop_json_filename=Settings.SRC_DIRECTORY +
            "Entities/Player/short_stop01_spritesheet.json",
            hard_stop_json_filename=Settings.SRC_DIRECTORY +
            "Entities/Player/hard_stop01_spritesheet.json",
            transition_frames=30,
            sound_json_filename=Settings.SRC_DIRECTORY + "Sound/Player/sounds.json"
        ),
        enemy_base=Enemy.Enemy(
            spritesheet_json_filename=Settings.SRC_DIRECTORY +
            "Entities/Enemy0/enemy0_spritesheet.json",
            spritesheet_scale=(1.75, 1.75),
            collider_offset=pygame.Vector2(57*0.875, 60*0.875),
            collider_size=pygame.Vector2(14*0.875, 34*0.875),
            weapons_collider_size=pygame.Vector2(40*0.875, 34*0.875),
            weapons_collider_offset=pygame.Vector2(17*0.875, 60*0.875),
            gravity=pygame.Vector2(0, 1600),
            walk_speed=50,
            alert_distance=110,
            calculate_flip=True,
        ),
        flying_enemy_base=Enemy.FlyingEnemy(
            spritesheet_json_filename=Settings.SRC_DIRECTORY +
            "Entities/Enemy1/enemy1_spritesheet.json",
            spritesheet_scale=(1.75, 1.75),
            collider_offset=pygame.Vector2(50*0.875, 50*0.875),
            collider_size=pygame.Vector2(24*0.875, 24*0.875),
            max_drift_distance=15,
            alert_distance=110,
            drift_speed=3,
            calculate_flip=True,
        ),
        water_base=Water.Water(
            waterbase_json_filename=Settings.SRC_DIRECTORY +
            "Entities/Water/waterbase_tileset.json",
            water_json_filename=Settings.SRC_DIRECTORY +
            "Entities/Water/water_spritesheet.json",
            water_bubbly_json_filename=Settings.SRC_DIRECTORY +
            "Entities/Water/water_bubbly_spritesheet.json",
            water_bubbliest_json_filename=Settings.SRC_DIRECTORY +
            "Entities/Water/water_bubbly_spritesheet.json",
            spritesheet_scale=(0.6, 0.6),
        ),
        toxic_water_base=Water.Water(
            waterbase_json_filename=Settings.SRC_DIRECTORY +
            "Entities/ToxicWater/waterbase_tileset.json",
            water_json_filename=Settings.SRC_DIRECTORY +
            "Entities/ToxicWater/water_spritesheet.json",
            water_bubbly_json_filename=Settings.SRC_DIRECTORY +
            "Entities/ToxicWater/water_bubbly_spritesheet.json",
            water_bubbliest_json_filename=Settings.SRC_DIRECTORY +
            "Entities/ToxicWater/water_bubbliest_spritesheet.json",
            spritesheet_scale=(0.6, 0.6),
        ),
        collectable_base=Enemy.ChallengeCollectable(
            spritesheet_json_filename=Settings.SRC_DIRECTORY +
            "Entities/Enemy2/enemy2_spritesheet.json",
            spritesheet_scale=(0.875,0.875),
            collider_offset=pygame.Vector2(22*0.875, 22*0.875),
            collider_size=pygame.Vector2(20*0.875, 20*0.875),
            max_float_distance=7,
            float_period=0.7,
        ),
    )
    debug_console = Console.Console(Settings.true_surface, level)
    return 1


def gameloop():
    is_running, is_paused, is_title, is_end_game = (True, False, True, False)
    damage_freeze = 0

    if is_title:
        Settings.gui.set_state("title")
    Settings.MUSIC["title"].Play(loops=-1)

    transition_frames = 0
    untransition_frames = Settings.TRANSITION_MAX_FRAMES
    while is_running:
        dt = Settings.clock.tick(60) / 1000  # Seconds elapsed

        # Handle events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    Settings.DEBUG = not Settings.DEBUG
                    print("Debug mode", ["off", "on"][Settings.DEBUG])
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_BACKQUOTE:
                    debug_console.console.toggle()

            elif event.type == pygame.QUIT:
                if not is_title:
                    level.save_game()
                return

            if event.type == pygame.VIDEORESIZE:
                old_surface_saved = Settings.true_surface
                Settings.true_surface = pygame.display.set_mode(
                    (event.w, event.h), pygame.RESIZABLE)
                Settings.true_surface.blit(old_surface_saved, (0, 0))
                del old_surface_saved

                Settings.gui_manager.mouse_pos_scale_factor = (
                    Settings.RESOLUTION[0] / event.w, Settings.RESOLUTION[1] / event.h)
                dt = 0

            Settings.gui_manager.process_events(event)
        Settings.gui_manager.update(dt)
        if debug_console.console.enabled:
            debug_console.console.update(events)

        prev_title = is_title
        is_running, is_paused, is_title, save, is_restart, name, leave_endgame = Settings.gui.handle_events(
            events)

        is_dialog = False
        for dialog in level.dialog_boxes:
            is_dialog = is_dialog or dialog.update(
                level, level.player.collider, level.name)
            dialog.process_events(events, level.name)

        is_paused = is_paused or debug_console.console.enabled

        if is_restart:
            return 1
        if prev_title and not is_title:
            transition_frames = Settings.TRANSITION_MAX_FRAMES
            Settings.SELECTED_SAVE = save
            level.load_save(save_num=Settings.SELECTED_SAVE)
            if not name is None:
                level.name = name
            Settings.MUSIC["ambient"].Play(loops=-1)
            Settings.MUSIC["title"].Stop(fade_out_ms=1000)
        if not prev_title and is_title:
            level.save_game()
            Settings.MUSIC["ambient"].Stop(fade_out_ms=1000)
            Settings.MUSIC["title"].Play(loops=-1)
        if leave_endgame is not None:
            is_end_game = False

        # Check whether display has been moved
        new_window_rect = Settings.get_window_rect()
        if not new_window_rect is None and not (new_window_rect.top == Settings.window_rect.top and new_window_rect.left == Settings.window_rect.left):
            dt = 0
        Settings.window_rect = new_window_rect

        if not is_title:
            # Handle physics and animations if unpaused
            if not is_paused and damage_freeze == 0 and not is_end_game:
                physical_colliders = level.get_colliders()
                attack_colliders = level.player.get_attack_colliders()
                damage_colliders = []

                i = 0
                hit_occured = False
                while i < len(level.enemies):
                    if level.enemies[i].state == "dead":
                        del level.enemies[i]
                    else:
                        level.enemies[i].update_state(level.player.position)
                        hit_occured = hit_occured or level.enemies[i].physics_process(
                            1/60, physical_colliders, level.player.position, attack_colliders)
                        damage_colliders += level.enemies[i].get_damage_colliders()
                        i += 1
                if hit_occured:
                    damage_freeze = 3


                state_changes = level.player.physics_process(1/60, physical_colliders, damage_colliders, level.get_hitable_colliders(
                ), level.get_death_colliders(), level.get_save_colliders(), level.get_water_colliders(), level.transitions, hit_occured, not is_dialog)
                if state_changes["respawn"]:
                    def end_animation(self):
                        level.load_level(level_name=level.save_level)
                        level.player.hearts = Settings.PLAYER_HEARTS
                        level.player.play_animation("unsit", speed=0.5)
                    level.player.play_animation(
                        "death", on_animation_end=end_animation)
                elif state_changes["reset"]:
                    level.player.play_animation(
                        "death", on_animation_end=lambda x: level.reset_level())
                elif not state_changes["transition"] == None:
                    transition_frames = Settings.TRANSITION_MAX_FRAMES
                elif state_changes["hit"]:
                    damage_freeze = 8
                if not is_dialog:
                    should_save = level.player.input(events)
                    if should_save:
                        Settings.gui.save_animation.play_animation("base")
                        level.player.hearts = Settings.PLAYER_HEARTS
                        level.save_level = level.level_name
                        level.save_dialog_completion = copy.deepcopy(
                            level.dialog_completion)
                        level.save_game()
                else:
                    level.player.input_static(events)

                i = 0
                while i < len(level.collectables):
                    if level.collectables[i].state == "death":
                        damage_freeze = 3
                        level.player.is_white = True
                    if level.collectables[i].physics_process(1/60, level.player.collider):
                        level.challenges.append(level.level_name)
                        del level.collectables[i]
                    else:
                        i += 1

                Settings.camera.update_position(dt, pygame.Vector2(level.player.collider.left, level.player.collider.top) + pygame.Vector2(
                    level.player.collider.size[0], 0), Settings.surface)
                _dt = dt
            else:
                level.player.input_static(events)
                _dt = 0

                if damage_freeze > 0:
                    damage_freeze -= 1

            # Render
            Settings.surface.fill((0, 0, 0))
            level.render_behind(_dt, Settings.surface,
                                Settings.camera.position)

            if not is_end_game:
                # Entities
                level.player.render(
                    Settings.surface, Settings.camera.position, delta=_dt)
                for enemy in level.enemies:
                    enemy.render(Settings.surface,
                                Settings.camera.position, delta=_dt)
                for collectable in level.collectables:
                    collectable.render(Settings.surface,
                                Settings.camera.position, delta=_dt)

            # Render frontground before gui
            level.render_infront(dt, Settings.surface,
                                 Settings.camera.position)

            # Debug rendering
            if Settings.DEBUG:
                level.render_colliders(
                    dt, Settings.surface, Settings.camera.position)
                level.player.render_colliders(
                    dt, Settings.surface, Settings.camera.position)
                for enemy in level.enemies:
                    enemy.render_colliders(
                        dt, Settings.surface, Settings.camera.position)
                for collectable in level.collectables:
                    collectable.render_colliders(
                        dt, Settings.surface, Settings.camera.position)

            if not is_end_game:
                # Ingame Gui rendering
                Settings.gui.render_ingame(
                    dt, Settings.surface, level.player, Settings.camera.position)

            # Handle screen fade transition
            if transition_frames > 0:
                transition_frames -= 1
                alpha = 255 - (transition_frames /
                               Settings.TRANSITION_MAX_FRAMES)*255
                Settings.surface.fill((0, 0, 0, alpha))
                if transition_frames == 0:
                    if not level.player.transition == None:
                        if level.player.transition["to_level"] == "EndGame":
                            is_end_game = True
                            level.load_level(
                                level_name=level.player.transition["to_level"], transition=level.player.transition)
                            Settings.gui.set_state("end_game")
                            level.name = Settings.DEFAULT_SAVE["name"]
                            level.has_begun = Settings.DEFAULT_SAVE["has_begun"]
                            level.save_level = Settings.DEFAULT_SAVE["save_level"]
                            level.save_dialog_completion = Settings.DEFAULT_SAVE["dialog_completion"]
                            level.save_game()
                            untransition_frames = 10*Settings.TRANSITION_MAX_FRAMES
                        else:
                            untransition_frames = Settings.TRANSITION_MAX_FRAMES
                            level.load_level(
                                level_name=level.player.transition["to_level"], transition=level.player.transition)
                        
            if untransition_frames > 0:
                untransition_frames -= 1
                if is_end_game:
                    alpha = (untransition_frames /
                         (Settings.TRANSITION_MAX_FRAMES*10))*255
                else:
                    alpha = (untransition_frames /
                            Settings.TRANSITION_MAX_FRAMES)*255
                Settings.surface.fill(
                    (0, 0, 0, alpha), special_flags=pygame.BLEND_RGBA_SUB)

            # Scale game rendering
            Settings.true_surface.blit(pygame.transform.scale(Settings.surface, (int(Settings.true_surface.get_rect().size[0]*Settings.camera.scale[0]), int(Settings.true_surface.get_rect().size[1]*Settings.camera.scale[1]))),
                                       (0, 0)
                                       )
            Settings.surface.fill((0, 0, 0, 0))
            for dialogue_box in level.dialog_boxes:
                dialogue_box.render(Settings.surface)

        Settings.gui.render(Settings.surface, Settings.camera.position, dt)
        Settings.gui_manager.draw_ui(Settings.surface)

        # Scale gui rendering
        Settings.true_surface.blit(pygame.transform.scale(
            Settings.surface, Settings.true_surface.get_rect().size), (0, 0))
        debug_console.console.show(Settings.true_surface)

        pygame.display.update()
    return 0


init()
while gameloop() == 1:
    if Settings.DEBUG:
        print("Reset display and recalculated gui")

    Settings.RESOLUTION_STR = Settings.USER_SETTINGS["resolution"]
    Settings.RESOLUTION = (int(Settings.RESOLUTION_STR.split(
        'x')[0]), int(Settings.RESOLUTION_STR.split('x')[1]))

    info = pygame.display.Info()
    screen_width, screen_height = info.current_w, info.current_h
    if platform.system() == "Windows":
        # https://gamedev.stackexchange.com/questions/105750/pygame-fullsreen-display-issue
        ctypes.windll.user32.SetProcessDPIAware()
        true_res = (ctypes.windll.user32.GetSystemMetrics(0),
                    ctypes.windll.user32.GetSystemMetrics(1))
        screen_width, screen_height = true_res
    Settings.is_fullscreen = Settings.USER_SETTINGS["fullscreen"]
    if Settings.USER_SETTINGS["fullscreen"]:
        Settings.true_surface = pygame.display.set_mode(
            (screen_width, screen_height), flags=pygame.FULLSCREEN)
    else:
        Settings.true_surface = pygame.display.set_mode(
            Settings.RESOLUTION, flags=pygame.RESIZABLE)

    Settings.surface = pygame.Surface(
        Settings.RESOLUTION, flags=pygame.SRCALPHA)
    Settings.window_rect = Settings.get_window_rect()

    Settings.gui_manager = pygame_gui.UIManager(
        Settings.RESOLUTION, Settings.SRC_DIRECTORY + "UI/pygamegui_theme.json")
    Settings.gui_manager.add_font_paths(
        "fff-forward", Settings.SRC_DIRECTORY + "UI/Fonts/pixel.ttf")
    Settings.gui = Gui.Gui(
        health_spritesheet_filename=Settings.SRC_DIRECTORY +
        "UI/Animations/health_spritesheet.json",
        health_sprite_filename=Settings.SRC_DIRECTORY+"UI/Images/health_bar_outline.png",
        title_background_filename=Settings.SRC_DIRECTORY +
        "UI/Animations/pixel_fog_spritesheet.json",
        title_animation_filename=Settings.SRC_DIRECTORY +
        "UI/Animations/title_logo_spritesheet.json",
        save_sprite_filename=Settings.SRC_DIRECTORY+"UI/Images/save.png",
        save_animation_filename=Settings.SRC_DIRECTORY +
        "UI/Animations/save_spritesheet.json",
    )

    Settings.gui_manager.mouse_pos_scale_factor = (
        Settings.RESOLUTION[0] / Settings.true_surface.get_width(), Settings.RESOLUTION[1] / Settings.true_surface.get_height())


try:
    os.makedirs(Settings.SRC_DIRECTORY+".cache")
except FileExistsError:
    pass

# Update sound cache
pickle.dump(Settings.MUSIC, open(
    Settings.SRC_DIRECTORY+".cache/music.p", mode="wb+"))
pickle.dump(Settings.SOUND_EFFECTS, open(
    Settings.SRC_DIRECTORY+".cache/sound_effects.p", mode="wb+"))
if Settings.DEBUG:
    print("wrote sound cache")

pygame.display.quit()
pygame.quit()
