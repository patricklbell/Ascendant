import os, sys, warnings, pickle
from typing import Set
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
warnings.simplefilter('ignore')
import pygame, json, pygame_gui
from Packages import  Settings, Sprite, Level, Camera, Player, Enemy, Gui, Water

level = None
def init():
    global level
    Settings.init()
    level = Level.Level(
        should_load=False,
        player_base=Player.Player(
            spritesheet_json_filename=Settings.SRC_DIRECTORY+"Entities/Player/player_spritesheet.json",
            spritesheet_scale=(2,2),
            collider_offset = pygame.Vector2(57, 60),
            collider_size = pygame.Vector2(14, 34),
            gravity = pygame.Vector2(0,1700),
            walk_speed=200,
            water_walk_speed=140,
            jump_speed=-350,
            jump_add_speed=-1600,
            jump_add_max_time=0.3,
            jump_grace_frames=4,
            knockback_speed=pygame.Vector2(500, 700),
            damage_knockback_speed=100,
            attack0_length=34,
            attack1_length=35,
            attack2_length=15,
            attack0_width=15,
            attack1_width=50,
            attack2_width=50,
            hearts=Settings.PLAYER_HEARTS,
            iframes=90,
            calculate_flip=True,
            calculate_white=True,
            water_splash_json_filename=Settings.SRC_DIRECTORY + "Entities/Water/splash.json",
            water_big_splash_json_filename=Settings.SRC_DIRECTORY + "Entities/Water/big_splash.json",
            short_stop_json_filename=Settings.SRC_DIRECTORY + "Entities/player/short_stop.json",
            hard_stop_json_filename=Settings.SRC_DIRECTORY + "Entities/player/hard_stop.json",
            transition_frames=30,
            sound_json_filename=Settings.SRC_DIRECTORY + "Sound/Player/sounds.json"
        ),
        enemy_base=Enemy.Enemy(
            spritesheet_json_filename=Settings.SRC_DIRECTORY+"Entities/Enemy0/enemy0_spritesheet.json",
            spritesheet_scale=(2,2),
            collider_offset = pygame.Vector2(57, 60),
            collider_size = pygame.Vector2(14, 34),
            weapons_collider_size = pygame.Vector2(40, 34),
            weapons_collider_offset = pygame.Vector2(17, 60),
            gravity = pygame.Vector2(0,1800),
            walk_speed=60, 
            alert_distance=150,
            calculate_flip=True,
        ),
        flying_enemy_base=Enemy.FlyingEnemy(
            spritesheet_json_filename=Settings.SRC_DIRECTORY+"Entities/Enemy1/enemy1_spritesheet.json",
            spritesheet_scale=(2,2),
            collider_offset = pygame.Vector2(50, 50),
            collider_size = pygame.Vector2(24, 24),
            max_drift_distance = 15,
            drift_speed = 3,
            calculate_flip=True,
        ),
        water_base=Water.Water(
            waterbase_json_filename=Settings.SRC_DIRECTORY+"Entities/Water/waterbase_tileset.json",
            water_json_filename=Settings.SRC_DIRECTORY+"Entities/Water/water.json",
            water_bubbly_json_filename=Settings.SRC_DIRECTORY+"Entities/Water/water_bubbly.json",
            water_bubbliest_json_filename=Settings.SRC_DIRECTORY+"Entities/Water/water_bubbliest.json",
            spritesheet_scale=(0.6,0.6),
        )
    )
    return 1

def gameloop():
    is_running, is_paused, is_title = (True, False, True)
    damage_freeze = 0

    Settings.gui.set_state(title=is_title)
    Settings.MUSIC["title"].Play(loops=-1)
    
    transition_frames = 0
    untransition_frames = Settings.TRANSITION_MAX_FRAMES
    redraw, redraw_frames =False, 0
    while is_running:
        dt = Settings.clock.tick(60) / 1000 # Seconds elapsed
        
        # Handle events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB: 
                    if Settings.DEBUG:
                        Settings.DEBUG = False
                        Settings.DEBUG_DIRTY_RECTS = True
                    elif Settings.DEBUG_DIRTY_RECTS:
                        Settings.DEBUG = False
                        Settings.DEBUG_DIRTY_RECTS = False
                    else:
                        Settings.DEBUG = True
                        Settings.DEBUG_DIRTY_RECTS = False

                    print("Debug mode", ["off", "on"][Settings.DEBUG])
                    print("Dirty Rect Debug mode", ["off", "on"][Settings.DEBUG_DIRTY_RECTS])

            if event.type == pygame.QUIT:
                if not is_title:
                    level.save_game()
                return
                
            if event.type == pygame.VIDEORESIZE:
                redraw = True
                old_surface_saved = Settings.true_surface
                Settings.true_surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                Settings.true_surface.blit(old_surface_saved, (0,0))
                del old_surface_saved

                Settings.gui_manager.mouse_pos_scale_factor = (Settings.RESOLUTION[0] / event.w, Settings.RESOLUTION[1] / event.h)
                print(Settings.gui_manager.mouse_pos_scale_factor)
                dt = 0

            Settings.gui_manager.process_events(event)
        Settings.gui_manager.update(dt)

        prev_title, prev_pause = is_title, is_paused
        is_running, is_paused, is_title, save, restart = Settings.gui.handle_events(events)
        if restart:
            return 1
        if not prev_pause == is_paused:
            redraw_frames = 2
        if prev_title == True and is_title == False:
            redraw = True
            transition_frames = Settings.TRANSITION_MAX_FRAMES
            Settings.SELECTED_SAVE = save
            level.load_save(save_num=Settings.SELECTED_SAVE)
            Settings.MUSIC["ambient"].Play(loops=-1)
            Settings.MUSIC["title"].Stop(fade_out_ms=1000)
        if prev_title == False and is_title == True:
            redraw = True
            level.save_game()
            Settings.MUSIC["ambient"].Stop(fade_out_ms=1000)
            Settings.MUSIC["title"].Play(loops=-1)
            
        # Check whether display has been moved
        new_window_rect = Settings.get_window_rect()
        if not new_window_rect == None and not (new_window_rect.top == Settings.window_rect.top and new_window_rect.left == Settings.window_rect.left):
            dt = 0
        Settings.window_rect = new_window_rect

        camera_moved = True
        if not is_title:
            # Handle physics and animations if unpaused
            if not is_paused and damage_freeze == 0:
                physical_colliders = level.get_colliders()
                attack_colliders = level.player.get_attack_colliders()
                damage_colliders = []
                
                i = 0
                hit_occured = False
                while i < len(level.enemies):
                    if level.enemies[i].state == "dead":
                        del level.enemies[i]
                        redraw = True
                    else:
                        level.enemies[i].update_state(level.player.position)
                        hit_occured = hit_occured or level.enemies[i].physics_process(1/60, physical_colliders, level.player.position, attack_colliders)
                        damage_colliders += level.enemies[i].get_damage_colliders()
                        i+=1
                if hit_occured:
                    damage_freeze = 3

                state_changes = level.player.physics_process(1/60, physical_colliders, damage_colliders, level.get_damage_colliders(), level.get_hitable_colliders(), level.get_save_colliders(), level.get_water_colliders(), level.transitions, hit_occured)
                if state_changes["respawn"]:
                    redraw_frames = 240
                    def end_animation(self):
                        level.load_level(level_num=level.save_level)
                        level.player.hearts = Settings.PLAYER_HEARTS
                        level.player.play_animation("unsit", speed=0.5)
                    level.player.play_animation("death", on_animation_end=end_animation)
                elif state_changes["reset"]:
                    redraw_frames = 240
                    level.player.play_animation("death", on_animation_end=lambda x: level.reset_level())
                elif not state_changes["transition"] == None:
                    redraw_frames = 240
                    transition_frames = Settings.TRANSITION_MAX_FRAMES
                elif state_changes["hit"]:
                    damage_freeze = 8
                
                should_save = level.player.input(events)
                if should_save:
                    Settings.gui.save_animation.play_animation("base")
                    level.save_level = level.level_num
                    level.save_game()
                

                camera_moved = Settings.camera.update_position(dt, level.player.position, Settings.surface)
            else:
                level.player.input_static(events)
                dt = 0

                if damage_freeze > 0:
                    damage_freeze-=1

            # Render
            dirty_rects = []
            Settings.surface.fill((0,0,0))
            level.render_behind(dt, Settings.surface, Settings.camera.position)

            # Entities
            dirty_rects += level.player.render(Settings.surface, Settings.camera.position, delta=dt)
            for enemy in level.enemies:
                dirty_rects += enemy.render(Settings.surface, Settings.camera.position, delta=dt)

            # Render frontground before gui
            dirty_rects += level.render_infront(dt, Settings.surface, Settings.camera.position)

            # Debug rendering
            if Settings.DEBUG:
                level.render_colliders(dt, Settings.surface, Settings.camera.position)
                dirty_rects += level.player.render_colliders(dt, Settings.surface, Settings.camera.position)
                for enemy in level.enemies:
                    dirty_rects += enemy.render_colliders(dt, Settings.surface, Settings.camera.position)
            
            # Ingame Gui rendering
            dirty_rects += Settings.gui.render_ingame(dt, Settings.surface, level.player, Settings.camera.position)

            # Handle screen fade transition
            if transition_frames > 0:
                redraw=True
                transition_frames -= 1
                alpha = 255 - (transition_frames / Settings.TRANSITION_MAX_FRAMES)*255
                Settings.surface.fill((0,0,0,alpha))
                if transition_frames == 0:
                    if not level.player.transition == None:
                        level.load_level(level_num=level.player.transition["to_level"], transition=level.player.transition)
                    untransition_frames = Settings.TRANSITION_MAX_FRAMES
            if untransition_frames > 0:
                redraw=True
                untransition_frames -= 1
                alpha = (untransition_frames / Settings.TRANSITION_MAX_FRAMES)*255
                Settings.surface.fill((0,0,0,alpha), special_flags=pygame.BLEND_RGBA_SUB)

        Settings.gui.render(Settings.surface, Settings.camera.position, dt)
        Settings.gui_manager.draw_ui(Settings.surface)

        # Scale to true display
        Settings.true_surface.blit(pygame.transform.scale(Settings.surface, Settings.true_surface.get_rect().size), (0, 0))

        if camera_moved or is_title or redraw or Settings.DEBUG or (redraw_frames > 0):
            pygame.display.update()
            redraw_frames = max(redraw_frames-1, 0)
            redraw=False
        else:
            # Note update function does not correctly handling dirty rects on windows
            scaleX, scaleY = Settings.true_surface.get_rect().width / Settings.surface.get_rect().width, Settings.true_surface.get_rect().height / Settings.surface.get_rect().height
            for rect in dirty_rects:
                # rect.inflate_ip(24, 24)
                # Scale to true display
                rect.update(rect.left*scaleX, rect.top*scaleY, rect.width*scaleX, rect.height*scaleY)

            if Settings.DEBUG_DIRTY_RECTS:
                for i in dirty_rects:
                    pygame.draw.rect(Settings.true_surface, (0,255,255), i)
                pygame.display.update()
            else:
                pygame.display.update(dirty_rects)
    return 0

def cleanup():
    pygame.display.quit()
    pygame.quit()

    # Update sound cache
    pickle.dump(Settings.MUSIC, open(Settings.SRC_DIRECTORY+".cache/music.p", mode="wb+"))
    pickle.dump(Settings.SOUND_EFFECTS, open(Settings.SRC_DIRECTORY+".cache/sound_effects.p", mode="wb+"))
    if Settings.DEBUG:
        print("wrote sound cache")

init()
while gameloop() == 1:
    if Settings.DEBUG:
        print("settings restart")
    cleanup()
    init()
cleanup()
