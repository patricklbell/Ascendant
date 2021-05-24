import pygame
import textboxify
from Packages import Settings
from string import Template


class Dialog():
    """ """

    def __init__(self, pages, collider, save_progress_name):
        self.collider = collider
        self.spn = save_progress_name

        self.pages = pages
        self.__construct_box(pages[0])
        self.page_index = 0

        self.dialog_group = pygame.sprite.LayeredDirty()
        self.has_activated = False

    def __construct_box(self, text):
        self.template = Template(text)
        self.dialog_box = textboxify.TextBoxFrame(
            border=textboxify.borders.LIGHT,
            font_name="arial",
            text=self.template.safe_substitute(name="example"),
            text_width=Settings.RESOLUTION[0]*0.5,
            lines=2,
            pos=(Settings.RESOLUTION[0]*(1/5), Settings.RESOLUTION[1]*(1/20)),
            padding=(Settings.RESOLUTION[0]/10, Settings.RESOLUTION[0]/15),
            font_color=(255, 255, 255),
            font_size=20,
            bg_color=(0, 0, 0),
        )
        self.dialog_box.set_indicator()
        self.dialog_box.set_portrait(Settings.SRC_DIRECTORY+"UI/Animations/player_portrait.png", (64, 64))

    def activate(self, player_name):
        """ """
        if not self.dialog_group:
            self.dialog_group.add(self.dialog_box)
        text = self.template.safe_substitute(name=player_name)
        if len(text) > 3 and text[0:3] == "...":
            self.dialog_box.set_portrait()
        self.dialog_box.set_text(text)
        self.has_activated = True

    def update(self, level, player_collider, player_name):
        """

        :param level: 
        :param player_collider: 

        """
        if not self.has_activated and self.collider.colliderect(player_collider) and (
            (self.spn not in level.save_dialog_completion) or (
                not level.save_dialog_completion[self.spn])
        ):
            self.activate(player_name)
            level.dialog_completion[self.spn] = True
            return True
        return self.dialog_group

    def process_events(self, events, player_name):
        """

        :param events: 

        """
        if self.dialog_group:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.key.key_code(Settings.USER_SETTINGS["bindings"]["dialog"]):
                        # Cleans the text box to be able to go on printing text
                        if self.dialog_box.words:
                            self.dialog_box.reset()

                        # Whole page has been printed and the box can now move pages
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
        """

        :param surface: 

        """
        self.dialog_group.draw(surface)
