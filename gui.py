import os

import toga
from toga.constants import COLUMN
from toga.style.pack import Pack
from togawizard import WizardBox, WizardScreen

import backend


class Epub2Anki(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name, size=(30, 30))

        anki_decks = backend.get_all_decks()
        state = {
            "epub_path": None,
            "anki_all_decks": anki_decks,
            "anki_selected_deck": None,
        }
        welcome_screen = FileChoosingScreen(state=state)
        info_screen = InfoScreen(state=state)

        wizard = WizardBox([welcome_screen, info_screen])
        wizard.style.update(flex=1)

        # use "enabled" instead of replacing contents?
        self.main_window.content = wizard
        self.main_window.content.style.update(padding=10)
        self.main_window.show()


class ScreenWithState(WizardScreen):
    def __init__(self, state):
        super().__init__()
        self._state = state


class InfoScreen(ScreenWithState):
    def construct_gui(self):
        epub_label = toga.Label("You chose {}".format(self._state["epub_path"]))
        main_box = toga.Box(children=[epub_label])
        self.add(main_box)


class FileChoosingScreen(ScreenWithState):
    def construct_gui(self):
        epub_label = toga.Label("Please choose the epub file", style=Pack(flex=1))
        self.epub_file_btn = toga.Button("Choose File", on_press=self.pressed_epub_btn)
        epub_box = toga.Box(
            children=[epub_label, self.epub_file_btn], style=Pack(padding_bottom=5)
        )

        anki_label = toga.Label("Which is your existing anki deck?", style=Pack(flex=1))
        anki_choice = toga.Selection(items=self._state["anki_all_decks"])
        anki_box = toga.Box(
            children=[anki_label, anki_choice], style=Pack(padding_bottom=5)
        )

        finished_btn = toga.Button("Finished", on_press=self.mark_finished)

        main_box = toga.Box(
            children=[epub_box, anki_box, finished_btn],
            style=Pack(direction=COLUMN, width=400),
        )

        self.add(main_box)

    def pressed_epub_btn(self, btn):
        app = self._parent_wizard.app
        epub_path = str(app.main_window.open_file_dialog("Choose epub"))

        if not epub_path.endswith(".epub"):
            app.main_window.error_dialog(
                "Invalid File Suffix",
                "The file doesn't end in .epub, and so I won't take it. Fight me >:{",
            )
            return

        self._state["epub_path"] = epub_path
        self.epub_file_btn.label = os.path.basename(epub_path)


if __name__ == "__main__":
    app = Epub2Anki("epub2anki", "de.thousandyardstare.epub2anki")
    app.main_loop()
