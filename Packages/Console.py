from Packages.Extern.pygame_console import game_console

class Console:
    def __init__(self, screen, level):
        self.level = level
        self.console = game_console.Console(self, screen.get_width(), {
            'global' : {
                'layout' : 'INPUT_BOTTOM',
                'padding' : (10,10,10,10),
                'bck_alpha' : 150,
                'welcome_msg' : 'Debug Console',
                'welcome_msg_color' : (0,255,0)
                },
            'input' : {
                'font_file' : 'Packages/Extern/pygame_console/fonts/JackInput.ttf',
                'bck_alpha' : 0
                },
            'output' : {
                'font_file' : 'Packages/Extern/pygame_console/fonts/JackInput.ttf',
                'bck_alpha' : 0,
                'display_lines' : 20,
                'display_columns' : 100
                }
            })