from Packages.Extern import SoundPlayer
from Packages import Sprite, Level, Camera, Player, Enemy, Gui, Water
import pygame, os, pygame_gui, json, platform, string, pickle


if platform.system() == "Windows":
    # For windows to get window rect
    from ctypes import POINTER, WINFUNCTYPE, windll
    from ctypes.wintypes import BOOL, HWND, RECT

# https://stackoverflow.com/questions/4135928/pygame-display-position
def get_window_rect():
    """ """
    if platform.system() == "Windows":
        # get our window ID:
        hwnd = pygame.display.get_wm_info()["window"]


        # Jump through all the ctypes hoops:
        prototype = WINFUNCTYPE(BOOL, HWND, POINTER(RECT))
        paramflags = (1, "hwnd"), (2, "lprect")

        GetWindowRect = prototype(("GetWindowRect", windll.user32), paramflags)

        # finally get our data!
        return GetWindowRect(hwnd)
    else:
        return None


def init():
    """ """
    # Setup constants
    global DEBUG, TRANSITION_MAX_FRAMES, DEBUG_DIRTY_RECTS, PLAYER_HEARTS, SELECTED_SAVE, DEFAULT_SAVE, CACHE
    PLAYER_HEARTS = 5
    TRANSITION_MAX_FRAMES = 30
    DEBUG = True
    CACHE = True
    DEBUG_DIRTY_RECTS = False
    SELECTED_SAVE = 0
    DEFAULT_SAVE = {
        "title_info": {
            "percentage_completion": 0.0
        },
        "save_level":1,
        "dialog_completion":{

        },
        "has_begun":0,
        "name":"",
    }
    
    # Load user settings and saves
    global SAVE_FILETEMPLATE, SRC_DIRECTORY, USER_SETTINGS, USER_SETTINGS_PATH, RESOLUTION, RESOLUTION_STR
    SRC_DIRECTORY = str(os.path.join(os.path.dirname(os.path.dirname(__file__)), "")).replace("\\", "/")
    USER_SETTINGS_PATH = SRC_DIRECTORY + "user_settings.json"
    SAVE_FILETEMPLATE = string.Template(SRC_DIRECTORY + "Saves/save$num.json")
    try:
        with open(USER_SETTINGS_PATH) as json_file:
                USER_SETTINGS = json.load(json_file)
    except:
        print("Failed to load", USER_SETTINGS_PATH)
        USER_SETTINGS = {
            "fullscreen": False,
            "bindings": {
                "attack": "z",
                "jump": "space",
                "left": "left",
                "right": "right",
                "up": "up",
                "down": "down",
                "dialog": "enter"
            },
            "resolution": "820x460",
            "music":True,
            "sound_effects":True
        }

    RESOLUTION_STR = USER_SETTINGS["resolution"]
    RESOLUTION = (int(RESOLUTION_STR.split('x')[0]), int(RESOLUTION_STR.split('x')[1]))
    
    
    # Setup pygame
    global surface, clock, camera, true_surface, window_rect, is_fullscreen
    pygame.init()
    icon = pygame.image.load(SRC_DIRECTORY + "UI/logo.png")
    pygame.display.set_icon(icon)
    pygame.display.set_caption("Ascendant")

    pygame.mouse.set_cursor(*pygame.cursors.load_xbm(SRC_DIRECTORY + "UI/cursor.xbm", SRC_DIRECTORY + "UI/cursor_mask.xbm"))

    info = pygame.display.Info()
    screen_width,screen_height = info.current_w,info.current_h
    is_fullscreen = USER_SETTINGS["fullscreen"]
    if USER_SETTINGS["fullscreen"]:
        true_surface = pygame.display.set_mode((screen_width, screen_height), flags=pygame.FULLSCREEN)   
    else:
        true_surface = pygame.display.set_mode(RESOLUTION, flags=pygame.RESIZABLE)

    surface = pygame.Surface(RESOLUTION, flags=pygame.SRCALPHA)
    window_rect = get_window_rect()

    clock = pygame.time.Clock()
    camera = Camera.Camera(position=pygame.Vector2(-1000,-400), max_move_speed=30, contraints_min=pygame.Vector2(0,0))
    
    # Setup GUI
    global gui_manager, gui
    gui_manager = pygame_gui.UIManager(RESOLUTION, SRC_DIRECTORY + "UI/pygamegui_theme.json")
    gui_manager.add_font_paths("fff-forward", SRC_DIRECTORY + "UI/Fonts/pixel.ttf")
    gui = Gui.Gui(
        health_spritesheet_filename=SRC_DIRECTORY+"UI/Animations/health_spritesheet.json",
        health_sprite_filename=SRC_DIRECTORY+"UI/Images/health_bar_outline.png",
        title_background_filename=SRC_DIRECTORY+"UI/Animations/pixel_fog_spritesheet.json",
        title_animation_filename=SRC_DIRECTORY+"UI/Animations/title_logo_spritesheet.json",
        save_sprite_filename=SRC_DIRECTORY+"UI/Images/save.png",
        save_animation_filename=SRC_DIRECTORY+"UI/Animations/save_spritesheet.json",
    )
    if USER_SETTINGS["fullscreen"]:
        gui_manager.mouse_pos_scale_factor = (RESOLUTION[0] / screen_width, RESOLUTION[1] / screen_height)


    # Load audio files and set volumes
    global MUSIC, SOUND_EFFECTS, MUSIC_VOLUMES, SOUND_EFFECTS_VOLUMES

    should_cache = False
    with open(SRC_DIRECTORY + "Sound/sounds.json") as json_file:
        json_data = json.load(json_file)

    if CACHE:
        if (os.path.exists(SRC_DIRECTORY+".cache/music.p") and 
            os.path.exists(SRC_DIRECTORY+".cache/sound_effects.p")):

            if DEBUG:
                print("loaded sound cache")
                
            MUSIC = pickle.load(open(SRC_DIRECTORY+".cache/music.p", mode="rb"))
            MUSIC_VOLUMES = {}
            for sounds in json_data["music"]:
                MUSIC_VOLUMES[sounds["name"]] = sounds["volume"]
            
            
            SOUND_EFFECTS = pickle.load(open(SRC_DIRECTORY+".cache/sound_effects.p", mode="rb"))
            SOUND_EFFECTS_VOLUMES = {}
            for sounds in json_data["sound_effects"]:
                SOUND_EFFECTS_VOLUMES[sounds["name"]] = sounds["volume"]
        else:
            should_cache = True
    
    if not CACHE or should_cache:
        SOUND_EFFECTS = {}
        SOUND_EFFECTS_VOLUMES = {}
        for sounds in json_data["sound_effects"]:
            SOUND_EFFECTS[sounds["name"]] = SoundPlayer.SoundPlayer(SRC_DIRECTORY + sounds["filename"])
            SOUND_EFFECTS_VOLUMES[sounds["name"]] = sounds["volume"]

            if USER_SETTINGS["sound_effects"]:
                SOUND_EFFECTS[sounds["name"]].SetVolume(USER_SETTINGS["sound_effects_volume"] * (sounds["volume"] / 100))
            else:
                SOUND_EFFECTS[sounds["name"]].SetVolume(0)
            
        MUSIC = {}
        MUSIC_VOLUMES = {}
        for sounds in json_data["music"]:
            MUSIC[sounds["name"]] = SoundPlayer.SoundPlayer(SRC_DIRECTORY + sounds["filename"])
            MUSIC_VOLUMES[sounds["name"]] = sounds["volume"]

            if USER_SETTINGS["music"]:
                MUSIC[sounds["name"]].SetVolume(USER_SETTINGS["music_volume"] * (sounds["volume"] / 100))
            else:
                MUSIC[sounds["name"]].SetVolume(0)
        
        if should_cache:
            pickle.dump(MUSIC, open(SRC_DIRECTORY+".cache/music.p", mode="wb+"))
            pickle.dump(SOUND_EFFECTS, open(SRC_DIRECTORY+".cache/sound_effects.p", mode="wb+"))

            if DEBUG:
                print("wrote sound cache")

    return 1