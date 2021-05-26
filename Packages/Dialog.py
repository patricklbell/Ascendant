import pygame
import os
import textboxify
from Packages import Settings
from string import Template


class Dialog():
    """ Manages creating, updating and rendering a single text box
    
    Args:
            pages ([str]): List of strings which contain different pages of dialog (required).
            collider (pygame.Rect): Level space rectangle describing where player entering to triggers dialog (required).
            save_progress_name (str): Name used in save file to track whether dialog has been seen (required).
    """

    def __init__(self, pages, collider, save_progress_name):
        # Setup properties
        self.collider = collider
        self.spn = save_progress_name

        self.pages = pages
        # Start by setting box to first page
        self.__construct_box(pages[0])
        self.page_index = 0

        self.dialog_group = pygame.sprite.LayeredDirty()

        # Initially dialog isnt active
        self.has_activated = False

    def __construct_box(self, text):
        """ Creates textbox and sets up first text
        
        Args:
            text (str): Message to display, can be a template string with $name (required).
        """
        # Create template with text to subsitute dynamic values
        self.template = Template(text)

        # Init text box with custom font and border
        self.dialog_box = textboxify.TextBoxFrame(
            border=textboxify.borders.LIGHT,
            font_name=os.path.abspath(Settings.SRC_DIRECTORY+"UI/Fonts/pixel.ttf"),
            text=self.template.safe_substitute(name="example"),
            text_width=Settings.RESOLUTION[0]*0.5,
            lines=2,
            pos=(Settings.RESOLUTION[0]*(1/5), Settings.RESOLUTION[1]*(1/20)),
            padding=(Settings.RESOLUTION[0]/10, Settings.RESOLUTION[0]/15),
            font_color=(255, 255, 255),
            font_size=14,
            bg_color=(0, 0, 0),
        )
        # Show indicator arrow and by default use player portrait
        self.dialog_box.set_indicator()
        self.dialog_box.set_portrait(Settings.SRC_DIRECTORY+"UI/Animations/player_portrait.png", (64, 64))

    def activate(self, player_name=""):
        """ Activates text box to be displayed 
        
        Args:
            player_name (str): Name to substitute into template strings.
        """
        # Add to display group if not already in it
        if not self.dialog_group:
            self.dialog_group.add(self.dialog_box)

        # Substitute player name and update dialog text
        text = self.template.safe_substitute(name=player_name)
        self.dialog_box.set_text(text)

        # Simple system for two voices, game messages are preceded by ... so show different portrait
        if len(text) > 3 and text[0:3] == "...":
            self.dialog_box.set_portrait(Settings.SRC_DIRECTORY+"UI/Animations/game_portrait.png", (64, 64))

        self.has_activated = True
    def update(self, level, player_collider, player_name=""):
        """ Activates dialog box if player has triggered the box.
        Returns True expression if dialog is currently active, if active returns dialog group

        Args:            
            level (Level.Level): Level object for updating state (required).
            player_collider (pygame.Rect): Rectangle collider describing player (required).
            player_name (str): Name to substitute into dialog template strings.
        """
        # Only activate if not already active, hasn't been activated in this playthrough and not saved as completed
        if not self.has_activated and self.collider.colliderect(player_collider) and (
            (self.spn not in level.save_dialog_completion) or (
                not level.save_dialog_completion[self.spn])
        ):
            self.activate(player_name)

            # Set level state so dialog not repeated in playthrough and polled to save
            level.dialog_completion[self.spn] = True
            return True
        return self.dialog_group

    def process_events(self, events, player_name=""):
        """ Process pygame events for dialog box

        Args:
            events ([pygame.events.Event]): List of pygame events to proccess (required).
            player_name (str): Name to substitute into dialog template strings.
        """
        if self.dialog_group:
            # Process events, based on textboxify examples: https://github.com/hnrkcode/TextBoxify
            for event in events:
                if event.type == pygame.KEYDOWN:
                    # Player tries to move to next page
                    if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["dialog"]):
                        # Cleans the text box to be able to go on printing text
                        if self.dialog_box.words:
                            self.dialog_box.reset()

                        # The page has been printed and the box can now move pages
                        else:
                            self.dialog_box.reset(hard=True)
                            self.dialog_box.kill()
                            self.page_index += 1
                            if self.page_index < len(self.pages):
                                self.__construct_box(
                                    self.pages[self.page_index])
                                self.activate(player_name)

            self.dialog_box.update()

    def render(self, surface):
        """ Draws dialog to surface if active

            Args:
                surface (pygame.Surface): Surface to render to in gui space (required).
        """
        self.dialog_group.draw(surface)
